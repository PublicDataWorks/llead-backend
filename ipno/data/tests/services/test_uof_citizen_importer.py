from unittest.mock import MagicMock

from django.test.testcases import TestCase, override_settings

from mock import Mock, patch

from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.factories import WrglRepoFactory
from data.models import ImportLog
from data.services import UofCitizenImporter
from use_of_forces.factories import UseOfForceCitizenFactory, UseOfForceFactory
from use_of_forces.models import UseOfForceCitizen


class UofImporterTestCase(TestCase):
    def setUp(self):
        self.header = [
            "uof_citizen_uid",
            "uof_uid",
            "citizen_influencing_factors",
            "citizen_distance_from_officer",
            "citizen_arrested",
            "citizen_arrest_charges",
            "citizen_hospitalized",
            "citizen_injured",
            "citizen_age",
            "citizen_race",
            "citizen_sex",
        ]
        self.uof_citizen_1_data = [
            "uof_citizen_uid1",
            "uof-uid1",
            "unknown",
            "0 feet to 1 feet",
            "yes",
            "",
            "no",
            "no",
            "30",
            "white",
            "male",
        ]
        self.uof_citizen_2_data = [
            "uof_citizen_uid2",
            "uof-uid2",
            "alchohol",
            "",
            "no",
            "",
            "no",
            "mentally unstable",
            "22",
            "asian",
            "female",
        ]
        self.uof_citizen_3_data = [
            "uof_citizen_uid3",
            "uof-uid3",
            "",
            "1 feet to 3 feet",
            "yes",
            "",
            "unknown",
            "unknown",
            "",
            "dark",
            "male",
        ]
        self.uof_citizen_4_data = [
            "uof_citizen_uid4",
            "uof-uid4",
            "none detected",
            "0 feet to 10 feet",
            "",
            "",
            "no",
            "",
            "13",
            "",
            "female",
        ]
        self.uof_citizen_5_data = [
            "uof_citizen_uid5",
            "uof-uid5",
            "alchohol",
            "",
            "yes",
            "",
            "no",
            "yes",
            "50",
            "spanish",
            "male",
        ]

        self.uof_citizen_5_dup_data = self.uof_citizen_5_data.copy()

        self.uof_citizens_data = [
            self.uof_citizen_1_data,
            self.uof_citizen_2_data,
            self.uof_citizen_3_data,
            self.uof_citizen_4_data,
            self.uof_citizen_5_data,
            self.uof_citizen_5_dup_data,
        ]

    @override_settings(WRGL_API_KEY="wrgl-api-key")
    @patch("data.services.base_importer.WRGL_USER", "wrgl_user")
    def test_process_successfully(self):
        use_of_force_1 = UseOfForceFactory(uof_uid="uof-uid1")
        use_of_force_2 = UseOfForceFactory(uof_uid="uof-uid2")
        use_of_force_3 = UseOfForceFactory(uof_uid="uof-uid3")
        use_of_force_4 = UseOfForceFactory(uof_uid="uof-uid4")
        use_of_force_5 = UseOfForceFactory(uof_uid="uof-uid5")

        UseOfForceCitizenFactory(
            uof_citizen_uid="uof_citizen_uid1",
            uof_uid="uof-uid1",
            use_of_force=use_of_force_1,
        )
        UseOfForceCitizenFactory(
            uof_citizen_uid="uof_citizen_uid2",
            uof_uid="uof-uid2",
            use_of_force=use_of_force_2,
        )
        UseOfForceCitizenFactory(
            uof_citizen_uid="uof_citizen_uid3",
            uof_uid="uof-uid3",
            use_of_force=use_of_force_3,
        )

        assert UseOfForceCitizen.objects.count() == 3

        WrglRepoFactory(
            data_model=UofCitizenImporter.data_model,
            repo_name="uof_citizen_repo",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
        )

        hash = "3950bd17edfd805972781ef9fe2c6449"

        uof_citizen_importer = UofCitizenImporter()

        uof_citizen_importer.branch = "main"

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        uof_citizen_importer.repo = Mock()
        uof_citizen_importer.new_commit = mock_commit

        uof_citizen_importer.retrieve_wrgl_data = Mock()

        uof_citizen_importer.old_column_mappings = {
            column: self.header.index(column) for column in self.header
        }
        uof_citizen_importer.column_mappings = {
            column: self.header.index(column) for column in self.header
        }

        processed_data = {
            "added_rows": [
                self.uof_citizen_4_data,
                self.uof_citizen_5_data,
                self.uof_citizen_5_dup_data,
            ],
            "deleted_rows": [
                self.uof_citizen_3_data,
            ],
            "updated_rows": [
                self.uof_citizen_1_data,
                self.uof_citizen_2_data,
            ],
        }

        uof_citizen_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = uof_citizen_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == UofCitizenImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == "3950bd17edfd805972781ef9fe2c6449"
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 2
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert UseOfForceCitizen.objects.count() == 4

        uof_citizen_importer.retrieve_wrgl_data.assert_called_with("uof_citizen_repo")

        check_columns = self.header + ["use_of_force_id"]
        check_columns_mappings = {
            column: check_columns.index(column) for column in check_columns
        }

        expected_uof_citizen_1_data = self.uof_citizen_1_data.copy()
        expected_uof_citizen_1_data.append(use_of_force_1.id)

        expected_uof_citizen_2_data = self.uof_citizen_2_data.copy()
        expected_uof_citizen_2_data.append(use_of_force_2.id)

        expected_uof_citizen_4_data = self.uof_citizen_4_data.copy()
        expected_uof_citizen_4_data.append(use_of_force_4.id)

        expected_uof_citizen_5_data = self.uof_citizen_5_data.copy()
        expected_uof_citizen_5_data.append(use_of_force_5.id)

        expected_uof_citizens_data = [
            expected_uof_citizen_1_data,
            expected_uof_citizen_2_data,
            expected_uof_citizen_4_data,
            expected_uof_citizen_5_data,
        ]

        for uof_citizen_data in expected_uof_citizens_data:
            uof_citizen = UseOfForceCitizen.objects.filter(
                uof_citizen_uid=uof_citizen_data[
                    check_columns_mappings["uof_citizen_uid"]
                ],
            ).first()

            assert uof_citizen

            field_attrs = [
                "uof_citizen_uid",
                "uof_uid",
                "citizen_influencing_factors",
                "citizen_distance_from_officer",
                "citizen_arrested",
                "citizen_arrest_charges",
                "citizen_hospitalized",
                "citizen_injured",
                "citizen_age",
                "citizen_race",
                "citizen_sex",
                "use_of_force_id",
            ]

            for attr in field_attrs:
                assert getattr(uof_citizen, attr) == (
                    uof_citizen_data[check_columns_mappings[attr]]
                    if uof_citizen_data[check_columns_mappings[attr]]
                    else None
                )

    @override_settings(WRGL_API_KEY="wrgl-api-key")
    @patch("data.services.base_importer.WRGL_USER", "wrgl_user")
    def test_process_successfully_with_columns_changed(self):
        use_of_force_1 = UseOfForceFactory(uof_uid="uof-uid1")
        use_of_force_2 = UseOfForceFactory(uof_uid="uof-uid2")
        use_of_force_3 = UseOfForceFactory(uof_uid="uof-uid3")
        use_of_force_4 = UseOfForceFactory(uof_uid="uof-uid4")
        use_of_force_5 = UseOfForceFactory(uof_uid="uof-uid5")

        UseOfForceCitizenFactory(
            uof_citizen_uid="uof_citizen_uid1",
            uof_uid="uof-uid1",
            use_of_force=use_of_force_1,
        )
        UseOfForceCitizenFactory(
            uof_citizen_uid="uof_citizen_uid2",
            uof_uid="uof-uid2",
            use_of_force=use_of_force_2,
        )
        UseOfForceCitizenFactory(
            uof_citizen_uid="uof_citizen_uid3",
            uof_uid="uof-uid3",
            use_of_force=use_of_force_3,
        )

        assert UseOfForceCitizen.objects.count() == 3

        WrglRepoFactory(
            data_model=UofCitizenImporter.data_model,
            repo_name="uof_citizen_repo",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
        )

        hash = "3950bd17edfd805972781ef9fe2c6449"

        uof_citizen_importer = UofCitizenImporter()

        uof_citizen_importer.branch = "main"

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        uof_citizen_importer.repo = Mock()
        uof_citizen_importer.new_commit = mock_commit

        uof_citizen_importer.retrieve_wrgl_data = Mock()

        old_columns = self.header[0:7] + self.header[8:]
        uof_citizen_importer.old_column_mappings = {
            column: old_columns.index(column) for column in old_columns
        }
        uof_citizen_importer.column_mappings = {
            column: self.header.index(column) for column in self.header
        }

        processed_data = {
            "added_rows": [
                self.uof_citizen_4_data,
                self.uof_citizen_5_data,
                self.uof_citizen_5_dup_data,
            ],
            "deleted_rows": [
                self.uof_citizen_3_data[0:7] + self.uof_citizen_3_data[8:],
            ],
            "updated_rows": [
                self.uof_citizen_1_data,
                self.uof_citizen_2_data,
            ],
        }

        uof_citizen_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = uof_citizen_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()

        assert import_log.data_model == UofCitizenImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == "3950bd17edfd805972781ef9fe2c6449"
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 2
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert UseOfForceCitizen.objects.count() == 4

        uof_citizen_importer.retrieve_wrgl_data.assert_called_with("uof_citizen_repo")

        check_columns = self.header + ["use_of_force_id"]
        check_columns_mappings = {
            column: check_columns.index(column) for column in check_columns
        }

        expected_uof_citizen_1_data = self.uof_citizen_1_data.copy()
        expected_uof_citizen_1_data.append(use_of_force_1.id)

        expected_uof_citizen_2_data = self.uof_citizen_2_data.copy()
        expected_uof_citizen_2_data.append(use_of_force_2.id)

        expected_uof_citizen_4_data = self.uof_citizen_4_data.copy()
        expected_uof_citizen_4_data.append(use_of_force_4.id)

        expected_uof_citizen_5_data = self.uof_citizen_5_data.copy()
        expected_uof_citizen_5_data.append(use_of_force_5.id)

        expected_uof_citizens_data = [
            expected_uof_citizen_1_data,
            expected_uof_citizen_2_data,
            expected_uof_citizen_4_data,
            expected_uof_citizen_5_data,
        ]

        for uof_citizen_data in expected_uof_citizens_data:
            uof_citizen = UseOfForceCitizen.objects.filter(
                uof_citizen_uid=uof_citizen_data[
                    check_columns_mappings["uof_citizen_uid"]
                ],
            ).first()

            assert uof_citizen

            field_attrs = [
                "uof_citizen_uid",
                "uof_uid",
                "citizen_influencing_factors",
                "citizen_distance_from_officer",
                "citizen_arrested",
                "citizen_arrest_charges",
                "citizen_hospitalized",
                "citizen_injured",
                "citizen_age",
                "citizen_race",
                "citizen_sex",
                "use_of_force_id",
            ]

            for attr in field_attrs:
                assert getattr(uof_citizen, attr) == (
                    uof_citizen_data[check_columns_mappings[attr]]
                    if uof_citizen_data[check_columns_mappings[attr]]
                    else None
                )

    def test_delete_non_existed_uof(self):
        WrglRepoFactory(
            data_model=UofCitizenImporter.data_model,
            repo_name="uof_citizen_repo",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
        )

        hash = "3950bd17edfd805972781ef9fe2c6449"

        uof_citizen_importer = UofCitizenImporter()

        uof_citizen_importer.branch = "main"

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        uof_citizen_importer.repo = Mock()
        uof_citizen_importer.new_commit = mock_commit

        uof_citizen_importer.retrieve_wrgl_data = Mock()

        uof_citizen_importer.old_column_mappings = {
            column: self.header.index(column) for column in self.header
        }
        uof_citizen_importer.column_mappings = {
            column: self.header.index(column) for column in self.header
        }

        processed_data = {
            "added_rows": [],
            "deleted_rows": [
                self.uof_citizen_3_data,
            ],
            "updated_rows": [],
        }

        uof_citizen_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = uof_citizen_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == UofCitizenImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == "3950bd17edfd805972781ef9fe2c6449"
        assert import_log.created_rows == 0
        assert import_log.updated_rows == 0
        assert import_log.deleted_rows == 0
        assert not import_log.error_message
        assert import_log.finished_at
