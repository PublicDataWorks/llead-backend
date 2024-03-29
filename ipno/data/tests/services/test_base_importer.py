from csv import DictWriter
from io import BytesIO, StringIO
from unittest.mock import MagicMock

from django.test.testcases import TestCase

import pytest
from mock import Mock, patch
from pytest import raises

from data.constants import (
    IMPORT_LOG_STATUS_ERROR,
    IMPORT_LOG_STATUS_FINISHED,
    IMPORT_LOG_STATUS_NO_NEW_COMMIT,
    IMPORT_LOG_STATUS_NO_NEW_DATA,
)
from data.factories import WrglRepoFactory
from data.models import ImportLog
from data.services import BaseImporter
from departments.factories import DepartmentFactory
from officers.factories import OfficerFactory
from officers.models import Officer
from use_of_forces.factories import UseOfForceFactory

TEST_MODEL_NAME = "TestModelName"


class TestImporter(BaseImporter):
    data_model = TEST_MODEL_NAME


class BaseImporterTestCase(TestCase):
    def setUp(self):
        csv_content = StringIO()
        writer = DictWriter(csv_content, fieldnames=["id", "name"])
        writer.writeheader()
        writer.writerows(
            [
                {
                    "id": "1",
                    "name": "name 1",
                },
                {
                    "id": "2",
                    "name": "name 2",
                },
                {
                    "id": "3",
                    "name": "name 3",
                },
            ]
        )
        self.csv_stream = BytesIO(csv_content.getvalue().encode("utf-8"))
        self.csv_text = csv_content.getvalue()
        self.tbi = TestImporter()

    def test_process_wrgl_repo_not_found(self):
        assert not TestImporter().process()

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == TEST_MODEL_NAME
        assert import_log.status == IMPORT_LOG_STATUS_ERROR
        assert import_log.error_message == "Cannot find Wrgl Repo!"
        assert import_log.finished_at

    def test_process_invalid_wrgl_repo_name(self):
        WrglRepoFactory(data_model=TEST_MODEL_NAME, repo_name="test_repo_name")

        self.tbi.branch = "main"

        mock_commit = MagicMock()
        mock_commit.table.columns = ["id", "uid"]
        mock_commit.sum = ""

        self.tbi.repo = Mock()
        self.tbi.new_commit = mock_commit

        self.tbi.retrieve_wrgl_data = Mock()

        assert not self.tbi.process()

        self.tbi.retrieve_wrgl_data.assert_called_with("test_repo_name")

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == TEST_MODEL_NAME
        assert import_log.status == IMPORT_LOG_STATUS_ERROR
        assert (
            import_log.error_message
            == "Cannot get latest commit hash from Wrgl for repo test_repo_name!"
        )
        assert import_log.finished_at

    def test_process_no_new_commit(self):
        hash = "3950bd17edfd805972781ef9fe2c6449"

        WrglRepoFactory(
            data_model=TEST_MODEL_NAME,
            repo_name="test_repo_name",
            commit_hash="3950bd17edfd805972781ef9fe2c6449",
            latest_commit_hash=hash,
        )

        self.tbi.branch = "main"

        mock_commit = MagicMock()
        mock_commit.table.columns = ["id", "uid"]
        mock_commit.sum = hash

        self.tbi.repo = Mock()
        self.tbi.new_commit = mock_commit

        self.tbi.retrieve_wrgl_data = Mock()

        assert not self.tbi.process()

        self.tbi.retrieve_wrgl_data.assert_called_with("test_repo_name")

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == TEST_MODEL_NAME
        assert import_log.status == IMPORT_LOG_STATUS_NO_NEW_COMMIT
        assert import_log.commit_hash == "3950bd17edfd805972781ef9fe2c6449"
        assert not import_log.error_message
        assert import_log.finished_at

    def test_process_error_while_processing_data(self):
        hash = "3950bd17edfd805972781ef9fe2c6449"

        WrglRepoFactory(
            data_model=TEST_MODEL_NAME,
            repo_name="test_repo_name",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
            latest_commit_hash=hash,
        )

        self.tbi.branch = "main"

        mock_commit = MagicMock()
        mock_commit.table.columns = ["id", "uid"]
        mock_commit.sum = hash

        self.tbi.repo = Mock()
        self.tbi.new_commit = mock_commit

        self.tbi.retrieve_wrgl_data = Mock()

        self.tbi.import_data = Exception()

        with pytest.raises(Exception):
            assert not self.tbi.process()

            assert self.tbi.retrieve_wrgl_data("test_repo_name")

            import_log = ImportLog.objects.order_by("-created_at").last()
            assert import_log.data_model == TEST_MODEL_NAME
            assert import_log.status == IMPORT_LOG_STATUS_ERROR
            assert import_log.commit_hash == "3950bd17edfd805972781ef9fe2c6449"
            assert "Error occurs while importing data!" in import_log.error_message
            assert import_log.finished_at

    def test_process_no_new_data(self):
        hash = "3950bd17edfd805972781ef9fe2c6449"

        WrglRepoFactory(
            data_model=TEST_MODEL_NAME,
            repo_name="test_repo_name",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
            latest_commit_hash=hash,
        )

        import_data_result = {
            "created_rows": 2,
            "updated_rows": 0,
            "deleted_rows": 1,
        }

        self.tbi.branch = "main"

        mock_commit = MagicMock()
        mock_commit.table.columns = ["id", "name"]
        mock_commit.sum = hash

        self.tbi.repo = Mock()
        self.tbi.new_commit = mock_commit

        self.tbi.retrieve_wrgl_data = Mock()

        self.tbi.import_data = Mock(return_value=import_data_result)

        self.tbi.process_wrgl_data = Mock(return_value=None)

        assert not self.tbi.process()

        assert self.tbi.retrieve_wrgl_data("test_repo_name")

        self.tbi.import_data.assert_not_called()

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == TEST_MODEL_NAME
        assert import_log.status == IMPORT_LOG_STATUS_NO_NEW_DATA
        assert import_log.commit_hash == "3950bd17edfd805972781ef9fe2c6449"
        assert not import_log.created_rows
        assert not import_log.updated_rows
        assert not import_log.deleted_rows
        assert not import_log.error_message
        assert import_log.finished_at

    def test_process_successfully(self):
        hash = "3950bd17edfd805972781ef9fe2c6449"

        WrglRepoFactory(
            data_model=TEST_MODEL_NAME,
            repo_name="test_repo_name",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
            latest_commit_hash=hash,
        )

        import_data_result = {
            "created_rows": 2,
            "updated_rows": 0,
            "deleted_rows": 1,
        }

        self.tbi.branch = "main"

        mock_commit = MagicMock()
        mock_commit.table.columns = ["id", "name"]
        mock_commit.sum = hash

        self.tbi.repo = Mock()
        self.tbi.new_commit = mock_commit

        self.tbi.retrieve_wrgl_data = Mock()

        self.tbi.import_data = Mock(return_value=import_data_result)

        processed_data = {
            "added_rows": [["1", "name 1"], ["3", "name 3"]],
            "deleted_rows": [
                ["2", "name 2"],
            ],
            "updated_rows": [],
        }

        self.tbi.process_wrgl_data = Mock(return_value=processed_data)

        assert self.tbi.process()

        assert self.tbi.retrieve_wrgl_data("test_repo_name")

        self.tbi.import_data.assert_called_with(processed_data)

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == TEST_MODEL_NAME
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == "3950bd17edfd805972781ef9fe2c6449"
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 0
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

    def test_process_successfully_without_current_commit_hash(self):
        hash = "3950bd17edfd805972781ef9fe2c6449"

        WrglRepoFactory(
            data_model=TEST_MODEL_NAME,
            repo_name="test_repo_name",
            commit_hash="",
            latest_commit_hash=hash,
        )

        import_data_result = {
            "created_rows": 2,
            "updated_rows": 0,
            "deleted_rows": 0,
        }

        self.tbi.branch = "main"

        mock_commit = MagicMock()
        mock_commit.table.columns = ["id", "name"]
        mock_commit.table.sum = hash
        mock_commit.sum = hash

        self.tbi.new_commit = mock_commit

        self.tbi.retrieve_wrgl_data = Mock()

        self.tbi.import_data = Mock(return_value=import_data_result)

        processed_data = {
            "added_rows": [["1", "name 1"], ["3", "name 3"]],
            "deleted_rows": [],
            "updated_rows": [],
        }

        self.tbi.process_wrgl_data = Mock()

        mock_get_blocks = Mock(return_value=processed_data.get("added_rows"))
        self.tbi.repo = Mock(get_blocks=mock_get_blocks)

        assert self.tbi.process()

        assert self.tbi.retrieve_wrgl_data("test_repo_name")

        self.tbi.process_wrgl_data.assert_not_called()
        self.tbi.repo.get_blocks.assert_called_with(
            "heads/test_repo_name", with_column_names=False
        )
        self.tbi.import_data.assert_called_with(processed_data)

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == TEST_MODEL_NAME
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == "3950bd17edfd805972781ef9fe2c6449"
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 0
        assert import_log.deleted_rows == 0
        assert not import_log.error_message
        assert import_log.finished_at

    @patch("data.services.base_importer.Repository")
    def test_retrieve_wrgl_data(self, mock_repository):
        mock_commit = MagicMock()
        mock_commit.table.columns = ["id", "name"]
        mock_get_branch = Mock(return_value=mock_commit)
        mock_repository.return_value = Mock(get_branch=mock_get_branch)

        self.tbi.branch = "main"
        self.tbi.retrieve_wrgl_data("branch_name")

        mock_get_branch.assert_called_with("branch_name")
        assert self.tbi.new_commit.table.columns == ["id", "name"]
        assert self.tbi.column_mappings == {"id": 0, "name": 1}

    def test_import_data(self):
        with raises(NotImplementedError):
            BaseImporter().import_data([])

    def test_department_mappings(self):
        department_1 = DepartmentFactory(agency_name="New Orleans PD")
        department_2 = DepartmentFactory(agency_name="Baton Rouge PD")

        mappings = BaseImporter().get_department_mappings()

        expected_mappings = {
            department_1.agency_slug: department_1.id,
            department_2.agency_slug: department_2.id,
        }
        assert mappings == expected_mappings

    def test_officer_mappings(self):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        mappings = BaseImporter().get_officer_mappings()
        expected_mappings = {
            officer_1.uid: officer_1.id,
            officer_2.uid: officer_2.id,
        }

        assert mappings == expected_mappings

    def test_uof_mappings(self):
        uof_1 = UseOfForceFactory()
        uof_2 = UseOfForceFactory()
        mappings = BaseImporter().get_uof_mappings()
        expected_mappings = {
            uof_1.uof_uid: uof_1.id,
            uof_2.uof_uid: uof_2.id,
        }

        assert mappings == expected_mappings

    def test_parse_row_data(self):
        self.tbi.ATTRIBUTES = ["id", "name", "year", "desc", "uid"]
        self.tbi.NA_ATTRIBUTES = ["desc"]
        self.tbi.INT_ATTRIBUTES = ["year"]

        column_mappings = {"id": 0, "name": 1, "year": 2, "desc": 3}

        row = ["1", "test", "2021", "NA"]

        result = self.tbi.parse_row_data(row, column_mappings)

        expected_result = {"id": "1", "name": "test", "year": 2021, "desc": None}

        assert result == expected_result

    def test_process_wrgl_data(self):
        mock_rows = [
            Mock(off1=1, off2=None),
            Mock(off1=None, off2=2),
            Mock(off1=3, off2=3),
        ]
        mock_diff = Mock(return_value=Mock(row_diff=mock_rows))
        mock_old_commit = MagicMock()
        mock_old_columns = ["id", "column 1"]
        mock_old_commit.table.columns = mock_old_columns

        mock_get_commit = Mock(return_value=mock_old_commit)
        mock_get_table_rows = Mock()

        def mock_get_table_rows_side_effect(table_sum, offs):
            if 1 in offs:
                return [["id1", "name1"]]
            elif 2 in offs:
                return [["id2", "name2"]]
            else:
                return [["id3", "name3"]]

        mock_get_table_rows.side_effect = mock_get_table_rows_side_effect

        self.tbi.repo = Mock(
            diff=mock_diff,
            get_commit=mock_get_commit,
            get_table_rows=mock_get_table_rows,
        )
        self.tbi.new_commit = Mock(sum="new_commit_hash")

        old_commit_hash = "dummy-old-commit-hash"
        result = self.tbi.process_wrgl_data(old_commit_hash)

        mock_diff.assert_called_with("new_commit_hash", "dummy-old-commit-hash")
        mock_get_commit.assert_called_with("dummy-old-commit-hash")

        expected_result = {
            "added_rows": [["id1", "name1"]],
            "deleted_rows": [["id2", "name2"]],
            "updated_rows": [["id3", "name3"]],
        }

        assert self.tbi.old_column_mappings == {"id": 0, "column 1": 1}
        assert result == expected_result

    def test_process_wrgl_data_no_row_diff_result(self):
        mock_diff = Mock(return_value=Mock(row_diff=None))

        self.tbi.repo = Mock(
            diff=mock_diff,
        )
        self.tbi.new_commit = Mock(sum="new_commit_hash")

        old_commit_hash = "dummy-old-commit-hash"
        result = self.tbi.process_wrgl_data(old_commit_hash)

        mock_diff.assert_called_with("new_commit_hash", "dummy-old-commit-hash")

        assert result is None

    def test_bulk_import(self):
        OfficerFactory()
        officer_2 = OfficerFactory()
        officer_3 = OfficerFactory()

        new_items_attrs = [
            {
                "uid": "abc",
                "first_name": "test_1",
            }
        ]

        self.tbi.UPDATE_ATTRIBUTES = ["first_name"]

        update_items_attrs = [
            {
                "id": officer_3.id,
                "first_name": "test_2",
            }
        ]

        delete_items_ids = [officer_2.id]

        result = self.tbi.bulk_import(
            Officer, new_items_attrs, update_items_attrs, delete_items_ids
        )

        expected_result = {"created_rows": 1, "updated_rows": 1, "deleted_rows": 1}

        assert result == expected_result

    def test_bulk_import_with_cleanup_action(self):
        OfficerFactory()
        officer_2 = OfficerFactory()
        officer_3 = OfficerFactory()

        new_items_attrs = [
            {
                "uid": "abc",
                "first_name": "test_1",
            }
        ]

        self.tbi.UPDATE_ATTRIBUTES = ["first_name"]

        update_items_attrs = [
            {
                "id": officer_3.id,
                "first_name": "test_2",
            }
        ]

        delete_items_ids = [officer_2.id]

        cleanup_action = Mock()

        delete_items_values = list(
            Officer.objects.filter(id__in=[officer_2.id]).values()
        )

        result = self.tbi.bulk_import(
            Officer,
            new_items_attrs,
            update_items_attrs,
            delete_items_ids,
            cleanup_action,
        )

        expected_result = {"created_rows": 1, "updated_rows": 1, "deleted_rows": 1}

        assert result == expected_result

        cleanup_action.assert_called_with(delete_items_values)
