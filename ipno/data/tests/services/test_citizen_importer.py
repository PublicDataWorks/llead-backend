from unittest.mock import MagicMock

from django.test.testcases import TestCase

from mock import Mock

from citizens.factory import CitizenFactory
from citizens.models import Citizen
from complaints.factories import ComplaintFactory
from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.factories import WrglRepoFactory
from data.models import ImportLog
from data.services import CitizenImporter
from departments.factories import DepartmentFactory
from use_of_forces.factories import UseOfForceFactory


class CitizenImporterTestCase(TestCase):
    def setUp(self):
        citizen_1 = CitizenFactory(
            citizen_uid="citizen_uid_1",
            allegation_uid="allegation_uid_1",
            uof_uid="uof_uid_1",
            agency="new-orleans-pd",
        )
        citizen_2 = CitizenFactory(
            citizen_uid="citizen_uid_2",
            allegation_uid="allegation_uid_2",
            uof_uid="uof_uid_2",
            agency="new-orleans-so",
        )
        citizen_3 = CitizenFactory(
            citizen_uid="citizen_uid_3",
            allegation_uid="allegation_uid_3",
            uof_uid="uof_uid_3",
            agency="kenner-pd",
        )
        citizen_4 = CitizenFactory(
            citizen_uid="citizen_uid_4",
            allegation_uid="allegation_uid_4",
            uof_uid="uof_uid_4",
            agency="bossier-parish-so",
        )
        citizen_5 = CitizenFactory(
            citizen_uid="citizen_uid_5",
            allegation_uid="allegation_uid_5",
            uof_uid="uof_uid_5",
            agency="louisiana-state-pd",
        )
        self.header = list(
            {field.name for field in Citizen._meta.fields}
            - Citizen.BASE_FIELDS
            - Citizen.CUSTOM_FIELDS
        )
        self.citizen_1_data = [getattr(citizen_1, field) for field in self.header]
        self.citizen_2_data = [getattr(citizen_2, field) for field in self.header]
        self.citizen_3_data = [getattr(citizen_3, field) for field in self.header]
        self.citizen_4_data = [getattr(citizen_4, field) for field in self.header]
        self.citizen_5_data = [getattr(citizen_5, field) for field in self.header]
        self.citizen_5_dup_data = self.citizen_5_data.copy()

        self.uof_citizens_data = [
            self.citizen_1_data,
            self.citizen_2_data,
            self.citizen_3_data,
            self.citizen_4_data,
            self.citizen_5_data,
            self.citizen_5_dup_data,
        ]

        Citizen.objects.all().delete()

    def test_process_successfully(self):
        department_1 = DepartmentFactory(agency_name="New Orleans PD")
        department_2 = DepartmentFactory(agency_name="New Orleans SO")
        department_3 = DepartmentFactory(agency_name="Kenner PD")
        department_4 = DepartmentFactory(agency_name="Bossier Parish SO")
        department_5 = DepartmentFactory(agency_name="Louisiana State PD")

        use_of_force_1 = UseOfForceFactory(uof_uid="uof_uid_1")
        use_of_force_2 = UseOfForceFactory(uof_uid="uof_uid_2")
        use_of_force_3 = UseOfForceFactory(uof_uid="uof_uid_3")
        use_of_force_4 = UseOfForceFactory(uof_uid="uof_uid_4")
        use_of_force_5 = UseOfForceFactory(uof_uid="uof_uid_5")

        complaint_1 = ComplaintFactory(allegation_uid="allegation_uid_1")
        complaint_2 = ComplaintFactory(allegation_uid="allegation_uid_2")
        complaint_3 = ComplaintFactory(allegation_uid="allegation_uid_3")
        complaint_4 = ComplaintFactory(allegation_uid="allegation_uid_4")
        complaint_5 = ComplaintFactory(allegation_uid="allegation_uid_5")

        CitizenFactory(
            citizen_uid="citizen_uid_1",
            use_of_force=use_of_force_1,
            complaint=complaint_1,
            department=department_1,
        )
        CitizenFactory(
            citizen_uid="citizen_uid_2",
            use_of_force=use_of_force_2,
            complaint=complaint_2,
            department=department_2,
        )
        CitizenFactory(
            citizen_uid="citizen_uid_3",
            use_of_force=use_of_force_3,
            complaint=complaint_3,
            department=department_3,
        )

        hash = "3950bd17edfd805972781ef9fe2c6449"

        assert Citizen.objects.count() == 3

        WrglRepoFactory(
            data_model=CitizenImporter.data_model,
            repo_name="citizen_repo",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
            latest_commit_hash=hash,
        )

        citizen_importer = CitizenImporter()

        citizen_importer.branch = "main"

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        citizen_importer.repo = Mock()
        citizen_importer.new_commit = mock_commit

        citizen_importer.retrieve_wrgl_data = Mock()

        citizen_importer.old_column_mappings = {
            column: self.header.index(column) for column in self.header
        }
        citizen_importer.column_mappings = {
            column: self.header.index(column) for column in self.header
        }

        processed_data = {
            "added_rows": [
                self.citizen_4_data,
                self.citizen_5_data,
                self.citizen_5_dup_data,
            ],
            "deleted_rows": [
                self.citizen_3_data,
            ],
            "updated_rows": [
                self.citizen_1_data,
                self.citizen_2_data,
            ],
        }

        citizen_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = citizen_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == CitizenImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == "3950bd17edfd805972781ef9fe2c6449"
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 2
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Citizen.objects.count() == 4

        citizen_importer.retrieve_wrgl_data.assert_called_with("citizen_repo")

        check_columns = self.header + [
            "department_id",
            "use_of_force_id",
            "complaint_id",
        ]
        check_columns_mappings = {
            column: check_columns.index(column) for column in check_columns
        }

        expected_citizen_1_data = self.citizen_1_data.copy()
        expected_citizen_1_data.append(department_1.id)
        expected_citizen_1_data.append(use_of_force_1.id)
        expected_citizen_1_data.append(complaint_1.id)

        expected_citizen_2_data = self.citizen_2_data.copy()
        expected_citizen_2_data.append(department_2.id)
        expected_citizen_2_data.append(use_of_force_2.id)
        expected_citizen_2_data.append(complaint_2.id)

        expected_citizen_4_data = self.citizen_4_data.copy()
        expected_citizen_4_data.append(department_4.id)
        expected_citizen_4_data.append(use_of_force_4.id)
        expected_citizen_4_data.append(complaint_4.id)

        expected_citizen_5_data = self.citizen_5_data.copy()
        expected_citizen_5_data.append(department_5.id)
        expected_citizen_5_data.append(use_of_force_5.id)
        expected_citizen_5_data.append(complaint_5.id)

        expected_citizens_data = [
            expected_citizen_1_data,
            expected_citizen_2_data,
            expected_citizen_4_data,
            expected_citizen_5_data,
        ]

        for citizen_data in expected_citizens_data:
            citizen = Citizen.objects.filter(
                citizen_uid=citizen_data[check_columns_mappings["citizen_uid"]],
            ).first()

            assert citizen

            field_attrs = [
                "citizen_uid",
                "allegation_uid",
                "uof_uid",
                "agency",
                "citizen_influencing_factors",
                "citizen_arrested",
                "citizen_hospitalized",
                "citizen_injured",
                "citizen_age",
                "citizen_race",
                "citizen_sex",
                "use_of_force_id",
                "complaint_id",
                "department_id",
            ]

            for attr in field_attrs:
                assert getattr(citizen, attr) == (
                    citizen_data[check_columns_mappings[attr]]
                    if citizen_data[check_columns_mappings[attr]]
                    else None
                )

    def test_process_successfully_with_columns_changed(self):
        department_1 = DepartmentFactory(agency_name="New Orleans PD")
        department_2 = DepartmentFactory(agency_name="New Orleans SO")
        department_3 = DepartmentFactory(agency_name="Kenner PD")
        department_4 = DepartmentFactory(agency_name="Bossier Parish SO")
        department_5 = DepartmentFactory(agency_name="Louisiana State PD")

        use_of_force_1 = UseOfForceFactory(uof_uid="uof_uid_1")
        use_of_force_2 = UseOfForceFactory(uof_uid="uof_uid_2")
        use_of_force_3 = UseOfForceFactory(uof_uid="uof_uid_3")
        use_of_force_4 = UseOfForceFactory(uof_uid="uof_uid_4")
        use_of_force_5 = UseOfForceFactory(uof_uid="uof_uid_5")

        complaint_1 = ComplaintFactory(allegation_uid="allegation_uid_1")
        complaint_2 = ComplaintFactory(allegation_uid="allegation_uid_2")
        complaint_3 = ComplaintFactory(allegation_uid="allegation_uid_3")
        complaint_4 = ComplaintFactory(allegation_uid="allegation_uid_4")
        complaint_5 = ComplaintFactory(allegation_uid="allegation_uid_5")

        CitizenFactory(
            citizen_uid="citizen_uid_1",
            use_of_force=use_of_force_1,
            complaint=complaint_1,
            department=department_1,
        )
        CitizenFactory(
            citizen_uid="citizen_uid_2",
            use_of_force=use_of_force_2,
            complaint=complaint_2,
            department=department_2,
        )
        CitizenFactory(
            citizen_uid="citizen_uid_3",
            use_of_force=use_of_force_3,
            complaint=complaint_3,
            department=department_3,
        )

        assert Citizen.objects.count() == 3

        hash = "3950bd17edfd805972781ef9fe2c6449"

        WrglRepoFactory(
            data_model=CitizenImporter.data_model,
            repo_name="citizen_repo",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
            latest_commit_hash=hash,
        )

        citizen_importer = CitizenImporter()

        citizen_importer.branch = "main"

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        citizen_importer.repo = Mock()
        citizen_importer.new_commit = mock_commit

        citizen_importer.retrieve_wrgl_data = Mock()

        old_columns = self.header[0:7] + self.header[8:]
        citizen_importer.old_column_mappings = {
            column: old_columns.index(column) for column in old_columns
        }
        citizen_importer.column_mappings = {
            column: self.header.index(column) for column in self.header
        }

        processed_data = {
            "added_rows": [
                self.citizen_4_data,
                self.citizen_5_data,
                self.citizen_5_dup_data,
            ],
            "deleted_rows": [
                self.citizen_3_data[0:7] + self.citizen_3_data[8:],
            ],
            "updated_rows": [
                self.citizen_1_data,
                self.citizen_2_data,
            ],
        }

        citizen_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = citizen_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()

        assert import_log.data_model == CitizenImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == "3950bd17edfd805972781ef9fe2c6449"
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 2
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Citizen.objects.count() == 4

        citizen_importer.retrieve_wrgl_data.assert_called_with("citizen_repo")

        check_columns = self.header + [
            "department_id",
            "use_of_force_id",
            "complaint_id",
        ]
        check_columns_mappings = {
            column: check_columns.index(column) for column in check_columns
        }

        expected_citizen_1_data = self.citizen_1_data.copy()
        expected_citizen_1_data.append(department_1.id)
        expected_citizen_1_data.append(use_of_force_1.id)
        expected_citizen_1_data.append(complaint_1.id)

        expected_citizen_2_data = self.citizen_2_data.copy()
        expected_citizen_2_data.append(department_2.id)
        expected_citizen_2_data.append(use_of_force_2.id)
        expected_citizen_2_data.append(complaint_2.id)

        expected_citizen_4_data = self.citizen_4_data.copy()
        expected_citizen_4_data.append(department_4.id)
        expected_citizen_4_data.append(use_of_force_4.id)
        expected_citizen_4_data.append(complaint_4.id)

        expected_citizen_5_data = self.citizen_5_data.copy()
        expected_citizen_5_data.append(department_5.id)
        expected_citizen_5_data.append(use_of_force_5.id)
        expected_citizen_5_data.append(complaint_5.id)

        expected_citizens_data = [
            expected_citizen_1_data,
            expected_citizen_2_data,
            expected_citizen_4_data,
            expected_citizen_5_data,
        ]

        for citizen_data in expected_citizens_data:
            citizen = Citizen.objects.filter(
                citizen_uid=citizen_data[check_columns_mappings["citizen_uid"]],
            ).first()

            assert citizen

            field_attrs = [
                "citizen_uid",
                "allegation_uid",
                "uof_uid",
                "agency",
                "citizen_influencing_factors",
                "citizen_arrested",
                "citizen_hospitalized",
                "citizen_injured",
                "citizen_age",
                "citizen_race",
                "citizen_sex",
                "use_of_force_id",
                "complaint_id",
                "department_id",
            ]

            for attr in field_attrs:
                assert getattr(citizen, attr) == (
                    citizen_data[check_columns_mappings[attr]]
                    if citizen_data[check_columns_mappings[attr]]
                    else None
                )

    def test_delete_non_existed_uof(self):
        hash = "3950bd17edfd805972781ef9fe2c6449"

        WrglRepoFactory(
            data_model=CitizenImporter.data_model,
            repo_name="citizen_repo",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
            latest_commit_hash=hash,
        )

        citizen_importer = CitizenImporter()

        citizen_importer.branch = "main"

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        citizen_importer.repo = Mock()
        citizen_importer.new_commit = mock_commit

        citizen_importer.retrieve_wrgl_data = Mock()

        citizen_importer.old_column_mappings = {
            column: self.header.index(column) for column in self.header
        }
        citizen_importer.column_mappings = {
            column: self.header.index(column) for column in self.header
        }

        processed_data = {
            "added_rows": [],
            "deleted_rows": [
                self.citizen_3_data,
            ],
            "updated_rows": [],
        }

        citizen_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = citizen_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == CitizenImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == "3950bd17edfd805972781ef9fe2c6449"
        assert import_log.created_rows == 0
        assert import_log.updated_rows == 0
        assert import_log.deleted_rows == 0
        assert not import_log.error_message
        assert import_log.finished_at
