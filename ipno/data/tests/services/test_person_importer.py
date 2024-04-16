from django.test.testcases import TestCase

from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.models import ImportLog
from data.services import PersonImporter
from data.util import MockDataReconciliation
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

        person_importer = PersonImporter("csv_file_path")

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
            "columns_mapping": {
                column: self.header.index(column) for column in self.header
            },
        }

        person_importer.data_reconciliation = MockDataReconciliation(processed_data)

        result = person_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()

        assert import_log.data_model == PersonImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert not import_log.commit_hash
        assert import_log.created_rows == 1
        assert import_log.updated_rows == 1
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Person.objects.count() == 2

        person1 = Person.objects.get(person_id="1")
        person3 = Person.objects.get(person_id="3")

        check_columns = person_importer.column_mappings.copy()

        expected_person1_data = self.person1_data.copy()
        assert person1.person_id == expected_person1_data[check_columns["person_id"]]
        assert (
            person1.canonical_officer.uid
            == expected_person1_data[check_columns["canonical_uid"]]
        )
        assert not person1.all_complaints_count
        assert expected_person1_data[
            check_columns["uids"]
        ] in person1.officers.values_list("uid", flat=True)
        assert (
            person1.canonical_uid
            == expected_person1_data[check_columns["canonical_uid"]]
        )
        assert person1.uids == expected_person1_data[check_columns["uids"]]

        expected_person3_data = self.person3_data.copy()
        assert person3.person_id == expected_person3_data[check_columns["person_id"]]
        assert (
            person3.canonical_officer.uid
            == expected_person3_data[check_columns["canonical_uid"]]
        )
        assert not person3.all_complaints_count
        expected_uids_list = person3.officers.values_list("uid", flat=True)
        assert expected_uids_list.count() == 1
        assert (
            expected_person3_data[check_columns["uids"]].split(",")[0]
            in expected_uids_list
        )
        assert (
            expected_person3_data[check_columns["uids"]].split(",")[1]
            not in expected_uids_list
        )
        assert (
            person3.canonical_uid
            == expected_person3_data[check_columns["canonical_uid"]]
        )
        assert person3.uids == expected_person3_data[check_columns["uids"]]

    def test_delete_non_existed_person(self):
        person_importer = PersonImporter("csv_file_path")

        person_importer.branch = "main"

        processed_data = {
            "added_rows": [],
            "deleted_rows": [
                self.person2_data,
            ],
            "updated_rows": [],
            "columns_mapping": {
                column: self.header.index(column) for column in self.header
            },
        }

        person_importer.data_reconciliation = MockDataReconciliation(processed_data)

        result = person_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()

        assert import_log.data_model == PersonImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert not import_log.commit_hash
        assert import_log.created_rows == 0
        assert import_log.updated_rows == 0
        assert import_log.deleted_rows == 0
        assert not import_log.error_message
        assert import_log.finished_at
