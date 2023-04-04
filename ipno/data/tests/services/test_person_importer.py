from unittest.mock import MagicMock

from django.test.testcases import TestCase

from mock import Mock

from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.factories import WrglRepoFactory
from data.models import ImportLog
from data.services import PersonImporter
from officers.factories import OfficerFactory
from people.factories import PersonFactory
from people.models import Person


class PersonImporterTestCase(TestCase):
    def setUp(self):
        self.header = ["person_id", "canonical_uid", "uids"]
        self.person1_data = [
            "1",
            "000526fa05739e97b61343513a92dbc7",
            "000526fa05739e97b61343513a92dbc7",
        ]
        self.person2_data = [
            "2",
            "0005624eee7c188d3604f2294dfb195d",
            "0005624eee7c188d3604f2294dfb195d,0007884f101d1661937abb130664d2d2",
        ]
        self.person3_data = [
            "3",
            "0007f3f6802b9fa493622d4a23edc00b",
            "0007f3f6802b9fa493622d4a23edc00b,0019ddf9abe0273e2d57215ec51697a1",
        ]
        self.person4_data = [
            "3",
            "0007f3f6802b9fa2d4a23edc00b",
            "0007f3f6802b9fa2d4a23edc00b",
        ]

        self.people_data = [
            self.person1_data,
            self.person2_data,
            self.person3_data,
            self.person4_data,
        ]

        self.officer1 = OfficerFactory(uid="000526fa05739e97b61343513a92dbc7")
        self.officer2 = OfficerFactory(uid="0005624eee7c188d3604f2294dfb195d")
        self.officer3 = OfficerFactory(uid="0007884f101d1661937abb130664d2d2")
        self.officer4 = OfficerFactory(uid="0007f3f6802b9fa493622d4a23edc00b")

    def test_process_successfully(self):
        updating_person = PersonFactory()
        updating_person.person_id = "1"
        updating_person.canonical_officer = self.officer4
        updating_person.officers.add(self.officer4)
        updating_person.save()

        deleting_person = PersonFactory()
        deleting_person.person_id = "2"
        deleting_person.canonical_officer = self.officer2
        deleting_person.officers.add(self.officer2)
        deleting_person.save()

        commit_hash = "3950bd17edfd805972781ef9fe2c6449"

        WrglRepoFactory(
            data_model=PersonImporter.data_model,
            repo_name="person_repo",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
            latest_commit_hash=commit_hash,
        )

        person_importer = PersonImporter()

        person_importer.branch = "main"

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = commit_hash

        person_importer.repo = Mock()
        person_importer.new_commit = mock_commit

        person_importer.retrieve_wrgl_data = Mock()

        person_importer.old_column_mappings = {
            column: self.header.index(column) for column in self.header
        }
        person_importer.column_mappings = {
            column: self.header.index(column) for column in self.header
        }

        processed_data = {
            "added_rows": [
                self.person3_data,
                self.person4_data,
            ],
            "deleted_rows": [
                self.person2_data,
            ],
            "updated_rows": [
                self.person1_data,
            ],
        }

        person_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = person_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()

        assert import_log.data_model == PersonImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == "3950bd17edfd805972781ef9fe2c6449"
        assert import_log.created_rows == 1
        assert import_log.updated_rows == 1
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Person.objects.count() == 2

        results = Person.objects.all()

        check_columns = person_importer.column_mappings.copy()

        person_importer.retrieve_wrgl_data.assert_called_with("person_repo")

        expected_person1_data = self.person1_data.copy()
        assert (
            results.first().person_id
            == expected_person1_data[check_columns["person_id"]]
        )
        assert (
            results.first().canonical_officer.uid
            == expected_person1_data[check_columns["canonical_uid"]]
        )
        assert not results.first().all_complaints_count
        assert expected_person1_data[
            check_columns["uids"]
        ] in results.first().officers.values_list("uid", flat=True)

        expected_person3_data = self.person3_data.copy()
        assert (
            results.last().person_id
            == expected_person3_data[check_columns["person_id"]]
        )
        assert (
            results.last().canonical_officer.uid
            == expected_person3_data[check_columns["canonical_uid"]]
        )
        assert not results.last().all_complaints_count
        expected_uids_list = results.last().officers.values_list("uid", flat=True)
        assert expected_uids_list.count() == 1
        assert (
            expected_person3_data[check_columns["uids"]].split(",")[0]
            in expected_uids_list
        )
        assert (
            expected_person3_data[check_columns["uids"]].split(",")[1]
            not in expected_uids_list
        )

    def test_delete_non_existed_person(self):
        commit_hash = "3950bd17edfd805972781ef9fe2c6449"

        WrglRepoFactory(
            data_model=PersonImporter.data_model,
            repo_name="person_repo",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
            latest_commit_hash=commit_hash,
        )

        person_importer = PersonImporter()

        person_importer.branch = "main"

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = commit_hash

        person_importer.repo = Mock()
        person_importer.new_commit = mock_commit

        person_importer.retrieve_wrgl_data = Mock()

        person_importer.old_column_mappings = {
            column: self.header.index(column) for column in self.header
        }
        person_importer.column_mappings = {
            column: self.header.index(column) for column in self.header
        }

        processed_data = {
            "added_rows": [],
            "deleted_rows": [
                self.person2_data,
            ],
            "updated_rows": [],
        }

        person_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = person_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()

        assert import_log.data_model == PersonImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == "3950bd17edfd805972781ef9fe2c6449"
        assert import_log.created_rows == 0
        assert import_log.updated_rows == 0
        assert import_log.deleted_rows == 0
        assert not import_log.error_message
        assert import_log.finished_at
