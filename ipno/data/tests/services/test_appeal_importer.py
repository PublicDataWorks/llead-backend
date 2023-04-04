from unittest.mock import MagicMock

from django.test.testcases import TestCase, override_settings

from mock import Mock

from appeals.factories import AppealFactory
from appeals.models import Appeal
from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.factories import WrglRepoFactory
from data.models import ImportLog
from data.services import AppealImporter
from departments.factories import DepartmentFactory
from officers.factories import OfficerFactory


class AppealImporterTestCase(TestCase):
    def setUp(self):
        appeal_1 = AppealFactory(
            appeal_uid="appeal_uid1",
            uid="officer-uid1",
            agency="new-orleans-pd",
        )
        appeal_2 = AppealFactory(
            appeal_uid="appeal_uid2",
            uid="officer-uid-invalid",
            agency="new-orleans-pd",
        )
        appeal_3 = AppealFactory(
            appeal_uid="appeal_uid3",
            uid="officer-uid2",
            agency="baton-rouge-pd",
        )
        appeal_4 = AppealFactory(
            appeal_uid="appeal_uid4",
            uid="",
            agency="new-orleans-pd",
        )
        appeal_5 = AppealFactory(
            appeal_uid="appeal_uid5",
            uid="officer-uid3",
            agency="baton-rouge-pd",
        )

        self.header = list(
            {field.name for field in Appeal._meta.fields}
            - Appeal.BASE_FIELDS
            - Appeal.CUSTOM_FIELDS
        )
        self.appeal1_data = [getattr(appeal_1, field) for field in self.header]
        self.appeal2_data = [getattr(appeal_2, field) for field in self.header]
        self.appeal3_data = [getattr(appeal_3, field) for field in self.header]
        self.appeal4_data = [getattr(appeal_4, field) for field in self.header]
        self.appeal5_data = [getattr(appeal_5, field) for field in self.header]
        self.appeal5_dup_data = self.appeal5_data.copy()

        self.appeals_data = [
            self.appeal1_data,
            self.appeal2_data,
            self.appeal3_data,
            self.appeal4_data,
            self.appeal5_data,
            self.appeal5_dup_data,
        ]
        Appeal.objects.all().delete()

    @override_settings(WRGL_API_KEY="wrgl-api-key")
    def test_process_successfully(self):
        AppealFactory(appeal_uid="appeal_uid1")
        AppealFactory(appeal_uid="appeal_uid2")
        AppealFactory(appeal_uid="appeal_uid3")

        department_1 = DepartmentFactory(agency_name="New Orleans PD")
        department_2 = DepartmentFactory(agency_name="Baton Rouge PD")

        officer_1 = OfficerFactory(uid="officer-uid1")
        OfficerFactory(uid="officer-uid2")
        officer_3 = OfficerFactory(uid="officer-uid3")

        assert Appeal.objects.count() == 3

        hash = "3950bd17edfd805972781ef9fe2c6449"

        WrglRepoFactory(
            data_model=AppealImporter.data_model,
            repo_name="appeal_repo",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
            latest_commit_hash=hash,
        )

        appeal_importer = AppealImporter()

        appeal_importer.branch = "main"

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        appeal_importer.repo = Mock()
        appeal_importer.new_commit = mock_commit

        appeal_importer.retrieve_wrgl_data = Mock()

        appeal_importer.old_column_mappings = {
            column: self.header.index(column) for column in self.header
        }
        appeal_importer.column_mappings = {
            column: self.header.index(column) for column in self.header
        }

        processed_data = {
            "added_rows": [
                self.appeal4_data,
                self.appeal5_data,
                self.appeal5_dup_data,
            ],
            "deleted_rows": [
                self.appeal3_data,
            ],
            "updated_rows": [
                self.appeal1_data,
                self.appeal2_data,
            ],
        }

        appeal_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = appeal_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == AppealImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == "3950bd17edfd805972781ef9fe2c6449"
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 2
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Appeal.objects.count() == 4

        appeal_importer.retrieve_wrgl_data.assert_called_with("appeal_repo")

        check_columns = self.header + ["department_id", "officer_id"]
        check_columns_mappings = {
            column: check_columns.index(column) for column in check_columns
        }

        expected_appeal1_data = self.appeal1_data.copy()
        expected_appeal1_data.append(department_1.id)
        expected_appeal1_data.append(officer_1.id)

        expected_appeal2_data = self.appeal2_data.copy()
        expected_appeal2_data.append(department_1.id)
        expected_appeal2_data.append(None)

        expected_appeal4_data = self.appeal4_data.copy()
        expected_appeal4_data.append(department_1.id)
        expected_appeal4_data.append(None)

        expected_appeal5_data = self.appeal5_data.copy()
        expected_appeal5_data.append(department_2.id)
        expected_appeal5_data.append(officer_3.id)

        expected_appeals_data = [
            expected_appeal1_data,
            expected_appeal2_data,
            expected_appeal4_data,
            expected_appeal5_data,
        ]

        for appeal_data in expected_appeals_data:
            appeal = Appeal.objects.filter(
                appeal_uid=appeal_data[check_columns_mappings["appeal_uid"]]
            ).first()
            assert appeal
            field_attrs = check_columns

            for attr in field_attrs:
                assert getattr(appeal, attr) == (
                    appeal_data[check_columns_mappings[attr]]
                    if appeal_data[check_columns_mappings[attr]]
                    else None
                )

    @override_settings(WRGL_API_KEY="wrgl-api-key")
    def test_process_successfully_with_columns_changed(self):
        AppealFactory(appeal_uid="appeal_uid1")
        AppealFactory(appeal_uid="appeal_uid2")
        AppealFactory(appeal_uid="appeal_uid3")

        department_1 = DepartmentFactory(agency_name="New Orleans PD")
        department_2 = DepartmentFactory(agency_name="Baton Rouge PD")

        officer_1 = OfficerFactory(uid="officer-uid1")
        OfficerFactory(uid="officer-uid2")
        officer_3 = OfficerFactory(uid="officer-uid3")

        assert Appeal.objects.count() == 3

        hash = "3950bd17edfd805972781ef9fe2c6449"

        WrglRepoFactory(
            data_model=AppealImporter.data_model,
            repo_name="appeal_repo",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
            latest_commit_hash=hash,
        )

        appeal_importer = AppealImporter()

        appeal_importer.branch = "main"

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        appeal_importer.repo = Mock()
        appeal_importer.new_commit = mock_commit

        appeal_importer.retrieve_wrgl_data = Mock()

        old_columns = self.header[0:7] + self.header[8:]
        appeal_importer.old_column_mappings = {
            column: old_columns.index(column) for column in old_columns
        }
        appeal_importer.column_mappings = {
            column: self.header.index(column) for column in self.header
        }

        processed_data = {
            "added_rows": [
                self.appeal4_data,
                self.appeal5_data,
                self.appeal5_dup_data,
            ],
            "deleted_rows": [
                self.appeal3_data[0:7] + self.appeal3_data[8:],
            ],
            "updated_rows": [
                self.appeal1_data,
                self.appeal2_data,
            ],
        }

        appeal_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = appeal_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == AppealImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == "3950bd17edfd805972781ef9fe2c6449"
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 2
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Appeal.objects.count() == 4

        appeal_importer.retrieve_wrgl_data.assert_called_with("appeal_repo")

        check_columns = self.header + ["department_id", "officer_id"]
        check_columns_mappings = {
            column: check_columns.index(column) for column in check_columns
        }

        expected_appeal1_data = self.appeal1_data.copy()
        expected_appeal1_data.append(department_1.id)
        expected_appeal1_data.append(officer_1.id)

        expected_appeal2_data = self.appeal2_data.copy()
        expected_appeal2_data.append(department_1.id)
        expected_appeal2_data.append(None)

        expected_appeal4_data = self.appeal4_data.copy()
        expected_appeal4_data.append(department_1.id)
        expected_appeal4_data.append(None)

        expected_appeal5_data = self.appeal5_data.copy()
        expected_appeal5_data.append(department_2.id)
        expected_appeal5_data.append(officer_3.id)

        expected_appeals_data = [
            expected_appeal1_data,
            expected_appeal2_data,
            expected_appeal4_data,
            expected_appeal5_data,
        ]

        for appeal_data in expected_appeals_data:
            appeal = Appeal.objects.filter(
                appeal_uid=appeal_data[check_columns_mappings["appeal_uid"]]
            ).first()
            assert appeal
            field_attrs = check_columns

            for attr in field_attrs:
                assert getattr(appeal, attr) == (
                    appeal_data[check_columns_mappings[attr]]
                    if appeal_data[check_columns_mappings[attr]]
                    else None
                )

    def test_delete_non_existed_uof(self):
        DepartmentFactory(agency_name="Baton Rouge PD")

        hash = "3950bd17edfd805972781ef9fe2c6449"

        WrglRepoFactory(
            data_model=AppealImporter.data_model,
            repo_name="uof_appeal",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
            latest_commit_hash=hash,
        )

        appeal_importer = AppealImporter()

        appeal_importer.branch = "main"

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        appeal_importer.repo = Mock()
        appeal_importer.new_commit = mock_commit

        appeal_importer.retrieve_wrgl_data = Mock()

        appeal_importer.old_column_mappings = {
            column: self.header.index(column) for column in self.header
        }
        appeal_importer.column_mappings = {
            column: self.header.index(column) for column in self.header
        }

        processed_data = {
            "added_rows": [],
            "deleted_rows": [
                self.appeal3_data,
            ],
            "updated_rows": [],
        }

        appeal_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = appeal_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == AppealImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == "3950bd17edfd805972781ef9fe2c6449"
        assert import_log.created_rows == 0
        assert import_log.updated_rows == 0
        assert import_log.deleted_rows == 0
        assert not import_log.error_message
        assert import_log.finished_at
