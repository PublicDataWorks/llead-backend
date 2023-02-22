from unittest.mock import MagicMock

from django.test.testcases import TestCase, override_settings

from mock import Mock

from complaints.factories import ComplaintFactory
from complaints.models import Complaint
from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.factories import WrglRepoFactory
from data.models import ImportLog
from data.services import ComplaintImporter
from departments.factories import DepartmentFactory
from officers.factories import OfficerFactory


class ComplaintImporterTestCase(TestCase):
    def setUp(self):
        complaint_1 = ComplaintFactory(
            allegation_uid="complaint-uid1-allegation-uid1-charge-uid1",
            uid="officer-uid1",
            agency="",
        )
        complaint_2 = ComplaintFactory(
            allegation_uid="complaint-uid1-allegation-uid1-charge-uid2",
            uid="officer-uid-invalid",
            agency="",
        )
        complaint_3 = ComplaintFactory(
            allegation_uid="complaint-uid1", uid="officer-uid2", agency="baton-rouge-pd"
        )
        complaint_4 = ComplaintFactory(
            allegation_uid="complaint-uid2-allegation-uid3",
            uid="",
            agency="new-orleans-pd",
        )
        complaint_5 = ComplaintFactory(
            allegation_uid="complaint-uid3-charge-uid2",
            uid="officer-uid3",
            agency="baton-rouge-pd",
        )
        complaint_6 = ComplaintFactory(
            allegation_uid="complaint-uid6-allegation-uid6-charge-uid2",
            uid="",
            agency="",
        )

        self.header = list(
            {field.name for field in Complaint._meta.fields}
            - Complaint.BASE_FIELDS
            - Complaint.CUSTOM_FIELDS
        )

        self.complaint1_data = [getattr(complaint_1, field) for field in self.header]
        self.complaint2_data = [getattr(complaint_2, field) for field in self.header]
        self.complaint3_data = [getattr(complaint_3, field) for field in self.header]
        self.complaint4_data = [getattr(complaint_4, field) for field in self.header]
        self.complaint5_data = [getattr(complaint_5, field) for field in self.header]
        self.complaint6_data = [getattr(complaint_6, field) for field in self.header]

        Complaint.objects.all().delete()

    @override_settings(WRGL_API_KEY="wrgl-api-key")
    def test_process_successfully(self):
        ComplaintFactory(allegation_uid="complaint-uid1-allegation-uid1-charge-uid1")
        ComplaintFactory(allegation_uid="complaint-uid1-allegation-uid1-charge-uid2")
        ComplaintFactory(allegation_uid="complaint-uid1")
        ComplaintFactory(allegation_uid="complaint-uid4")
        ComplaintFactory(allegation_uid="complaint-uid6-allegation-uid6-charge-uid2")

        department_1 = DepartmentFactory(agency_name="New Orleans PD")
        department_2 = DepartmentFactory(agency_name="Baton Rouge PD")

        officer_1 = OfficerFactory(uid="officer-uid1")
        OfficerFactory(uid="officer-uid2")
        officer_3 = OfficerFactory(uid="officer-uid3")

        assert Complaint.objects.count() == 5

        hash = "3950bd17edfd805972781ef9fe2c6449"

        WrglRepoFactory(
            data_model=ComplaintImporter.data_model,
            repo_name="complaint_repo",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
            latest_commit_hash=hash,
        )

        complaint_importer = ComplaintImporter()

        complaint_importer.branch = "main"

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        complaint_importer.repo = Mock()
        complaint_importer.new_commit = mock_commit

        complaint_importer.retrieve_wrgl_data = Mock()

        complaint_importer.old_column_mappings = {
            column: self.header.index(column) for column in self.header
        }
        complaint_importer.column_mappings = {
            column: self.header.index(column) for column in self.header
        }

        processed_data = {
            "added_rows": [self.complaint4_data, self.complaint5_data],
            "deleted_rows": [
                self.complaint3_data,
            ],
            "updated_rows": [
                self.complaint1_data,
                self.complaint2_data,
                self.complaint6_data,
            ],
        }

        complaint_importer.process_wrgl_data = Mock(return_value=processed_data)

        complaint_importer.process()

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == ComplaintImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == "3950bd17edfd805972781ef9fe2c6449"
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 3
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Complaint.objects.count() == 6

        complaint_importer.retrieve_wrgl_data.assert_called_with("complaint_repo")

        check_columns = self.header + ["department_ids", "officer_ids"]
        check_columns_mappings = {
            column: check_columns.index(column) for column in check_columns
        }

        expected_complaint1_data = self.complaint1_data.copy()
        expected_complaint1_data.append([])
        expected_complaint1_data.append([officer_1.id])

        expected_complaint2_data = self.complaint2_data.copy()
        expected_complaint2_data.append([])
        expected_complaint2_data.append([])

        expected_complaint4_data = self.complaint4_data.copy()
        expected_complaint4_data.append([department_1.id])
        expected_complaint4_data.append([])

        expected_complaint5_data = self.complaint5_data.copy()
        expected_complaint5_data.append([department_2.id])
        expected_complaint5_data.append([officer_3.id])

        expected_complaint6_data = self.complaint6_data.copy()
        expected_complaint6_data.append([])
        expected_complaint6_data.append([])

        expected_complaints_data = [
            expected_complaint1_data,
            expected_complaint2_data,
            expected_complaint4_data,
            expected_complaint5_data,
        ]

        for complaint_data in expected_complaints_data:
            complaint = Complaint.objects.filter(
                allegation_uid=complaint_data[check_columns_mappings["allegation_uid"]]
                if complaint_data[check_columns_mappings["allegation_uid"]]
                else None
            ).first()
            assert complaint
            field_attrs = self.header

            for attr in field_attrs:
                assert getattr(complaint, attr) == (
                    complaint_data[check_columns_mappings[attr]]
                    if complaint_data[check_columns_mappings[attr]]
                    else None
                )

            assert (
                list(complaint.departments.values_list("id", flat=True))
                == complaint_data[check_columns_mappings["department_ids"]]
            )
            assert (
                list(complaint.officers.values_list("id", flat=True))
                == complaint_data[check_columns_mappings["officer_ids"]]
            )

    @override_settings(WRGL_API_KEY="wrgl-api-key")
    def test_process_successfully_with_column_changed(self):
        ComplaintFactory(allegation_uid="complaint-uid1-allegation-uid1-charge-uid1")
        ComplaintFactory(allegation_uid="complaint-uid1-allegation-uid1-charge-uid2")
        ComplaintFactory(allegation_uid="complaint-uid1")
        ComplaintFactory(allegation_uid="complaint-uid4")
        ComplaintFactory(allegation_uid="complaint-uid6-allegation-uid6-charge-uid2")

        department_1 = DepartmentFactory(agency_name="New Orleans PD")
        department_2 = DepartmentFactory(agency_name="Baton Rouge PD")

        officer_1 = OfficerFactory(uid="officer-uid1")
        OfficerFactory(uid="officer-uid2")
        officer_3 = OfficerFactory(uid="officer-uid3")

        assert Complaint.objects.count() == 5

        hash = "3950bd17edfd805972781ef9fe2c6449"

        WrglRepoFactory(
            data_model=ComplaintImporter.data_model,
            repo_name="complaint_repo",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
            latest_commit_hash=hash,
        )

        complaint_importer = ComplaintImporter()

        complaint_importer.branch = "main"

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        complaint_importer.repo = Mock()
        complaint_importer.new_commit = mock_commit

        complaint_importer.retrieve_wrgl_data = Mock()

        deleted_index = self.header.index("disposition")
        old_columns = self.header[0:deleted_index] + self.header[deleted_index + 1 :]
        complaint_importer.old_column_mappings = {
            column: old_columns.index(column) for column in old_columns
        }
        complaint_importer.column_mappings = {
            column: self.header.index(column) for column in self.header
        }

        processed_data = {
            "added_rows": [self.complaint4_data, self.complaint5_data],
            "deleted_rows": [
                self.complaint3_data[0:deleted_index]
                + self.complaint3_data[deleted_index + 1 :],
            ],
            "updated_rows": [
                self.complaint1_data,
                self.complaint2_data,
                self.complaint6_data,
            ],
        }

        complaint_importer.process_wrgl_data = Mock(return_value=processed_data)
        complaint_importer.process()

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == ComplaintImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == "3950bd17edfd805972781ef9fe2c6449"
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 3
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Complaint.objects.count() == 6

        complaint_importer.retrieve_wrgl_data.assert_called_with("complaint_repo")

        check_columns = self.header + ["department_ids", "officer_ids"]
        check_columns_mappings = {
            column: check_columns.index(column) for column in check_columns
        }

        expected_complaint1_data = self.complaint1_data.copy()
        expected_complaint1_data.append([])
        expected_complaint1_data.append([officer_1.id])

        expected_complaint2_data = self.complaint2_data.copy()
        expected_complaint2_data.append([])
        expected_complaint2_data.append([])

        expected_complaint4_data = self.complaint4_data.copy()
        expected_complaint4_data.append([department_1.id])
        expected_complaint4_data.append([])

        expected_complaint5_data = self.complaint5_data.copy()
        expected_complaint5_data.append([department_2.id])
        expected_complaint5_data.append([officer_3.id])

        expected_complaint6_data = self.complaint6_data.copy()
        expected_complaint6_data.append([])
        expected_complaint6_data.append([])

        expected_complaints_data = [
            expected_complaint1_data,
            expected_complaint2_data,
            expected_complaint4_data,
            expected_complaint5_data,
        ]

        for complaint_data in expected_complaints_data:
            complaint = Complaint.objects.filter(
                allegation_uid=complaint_data[check_columns_mappings["allegation_uid"]]
                if complaint_data[check_columns_mappings["allegation_uid"]]
                else None
            ).first()
            assert complaint
            field_attrs = self.header

            for attr in field_attrs:
                assert getattr(complaint, attr) == (
                    complaint_data[check_columns_mappings[attr]]
                    if complaint_data[check_columns_mappings[attr]]
                    else None
                )

            assert (
                list(complaint.departments.values_list("id", flat=True))
                == complaint_data[check_columns_mappings["department_ids"]]
            )
            assert (
                list(complaint.officers.values_list("id", flat=True))
                == complaint_data[check_columns_mappings["officer_ids"]]
            )

    def test_handle_record_data_with_duplicate_uid(self):
        complaint_importer = ComplaintImporter()

        complaint_importer.new_allegation_uids = ["allegation-uid"]

        complaint_importer.parse_row_data = Mock()
        complaint_importer.parse_row_data.return_value = {
            "allegation_uid": "allegation-uid",
        }

        complaint_importer.handle_record_data("row")

        assert complaint_importer.new_allegation_uids == ["allegation-uid"]
