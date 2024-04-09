from django.test.testcases import TestCase

from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.models import ImportLog
from data.services import OfficerImporter
from data.util import MockDataReconciliation
from departments.factories import DepartmentFactory
from officers.factories import OfficerFactory
from officers.models import Officer


class OfficerImporterTestCase(TestCase):
    def setUp(self):
        officer_1 = OfficerFactory(
            uid="uid_1",
            agency="new-orleans-pd",
            first_name="Emile",
            last_name="Sanchez",
        )
        officer_2 = OfficerFactory(
            uid="uid_2",
            agency="louisiana-state-pd",
            first_name="Anthony",
            last_name="Monaco",
        )
        officer_3 = OfficerFactory(
            uid="uid_3",
            agency="new-orleans-pd",
            first_name="Joel",
            last_name="Maier",
        )
        officer_4 = OfficerFactory(
            uid="uid_4",
            agency="new-orleans-so",
        )
        officer_5 = OfficerFactory(uid="uid_5", agency="baton-rouge-pd")
        officer_6 = OfficerFactory(uid="uid_6", agency="lafayette-pd")

        self.header = list(
            {field.name for field in Officer._meta.fields}
            - Officer.BASE_FIELDS
            - Officer.CUSTOM_FIELDS
        )
        self.officer1_data = [getattr(officer_1, field) for field in self.header]
        self.officer2_data = [getattr(officer_2, field) for field in self.header]
        self.officer3_data = [getattr(officer_3, field) for field in self.header]
        self.officer4_data = [getattr(officer_4, field) for field in self.header]
        self.officer5_data = [getattr(officer_5, field) for field in self.header]
        self.officer6_data = [getattr(officer_6, field) for field in self.header]
        self.officer5_dup_data = self.officer5_data.copy()

        DepartmentFactory(agency_name="New Orleans PD")
        DepartmentFactory(agency_name="Louisiana State PD")
        DepartmentFactory(agency_name="New Orleans SO")
        DepartmentFactory(agency_name="Baton Rouge PD")
        DepartmentFactory(agency_name="Jefferson SO")
        DepartmentFactory(agency_name="Lafayette PD")

        Officer.objects.all().delete()

    def test_process_successfully(self):
        OfficerFactory(
            uid="uid_1",
            first_name="Emile",
            last_name="Sanchez",
        )
        OfficerFactory(
            uid="uid_2",
            first_name="Anthony",
            last_name="Monaco",
        )
        OfficerFactory(
            uid="uid_3",
            first_name="Joel",
            last_name="Maier",
        )
        OfficerFactory(uid="uid_6")

        assert Officer.objects.count() == 4

        officer_importer = OfficerImporter("csv_file_path")

        processed_data = {
            "added_rows": [
                self.officer4_data,
                self.officer5_data,
                self.officer5_dup_data,
            ],
            "deleted_rows": [
                self.officer6_data,
            ],
            "updated_rows": [
                self.officer1_data,
                self.officer2_data,
                self.officer3_data,
            ],
            "columns_mapping": {
                column: self.header.index(column) for column in self.header
            },
        }

        officer_importer.data_reconciliation = MockDataReconciliation(processed_data)

        result = officer_importer.process()

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == OfficerImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert not import_log.commit_hash
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 3
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Officer.objects.count() == 5

        assert result

        check_columns = officer_importer.column_mappings.copy()

        officers_data = [
            self.officer1_data,
            self.officer2_data,
            self.officer3_data,
            self.officer4_data,
            self.officer5_data,
        ]

        for officer_data in officers_data:
            officer = Officer.objects.filter(
                uid=officer_data[check_columns["uid"]]
            ).first()
            assert officer
            field_attrs = [
                "last_name",
                "middle_name",
                "first_name",
                "race",
                "sex",
            ]
            integer_field_attrs = [
                "birth_year",
                "birth_month",
                "birth_day",
            ]

            for attr in field_attrs:
                assert getattr(officer, attr) == (
                    officer_data[check_columns[attr]]
                    if officer_data[check_columns[attr]]
                    else None
                )

            for attr in integer_field_attrs:
                assert getattr(officer, attr) == (
                    int(officer_data[check_columns[attr]])
                    if officer_data[check_columns[attr]]
                    else None
                )

    def test_get_officer_name_mappings(self):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()

        officer_importer = OfficerImporter("csv_file_path")
        result = officer_importer.get_officer_name_mappings()

        expected_result = {
            officer_1.uid: (officer_1.first_name, officer_1.last_name),
            officer_2.uid: (officer_2.first_name, officer_2.last_name),
        }

        assert result == expected_result

    def test_process_update_officer_name_successfully(self):
        OfficerFactory(
            uid="uid_1",
            first_name="Emile",
            last_name="Sanchez",
            is_name_changed=False,
        )
        OfficerFactory(
            uid="uid_2",
            first_name="Anthony",
            last_name="Monac",
            is_name_changed=False,
        )
        OfficerFactory(
            uid="uid_3",
            first_name="Maier",
            last_name="Joe",
            is_name_changed=False,
        )
        OfficerFactory(uid="uid_6")

        assert Officer.objects.count() == 4

        officer_importer = OfficerImporter("csv_file_path")

        processed_data = {
            "added_rows": [
                self.officer4_data,
                self.officer5_data,
                self.officer5_dup_data,
            ],
            "deleted_rows": [
                self.officer6_data,
            ],
            "updated_rows": [
                self.officer1_data,
                self.officer2_data,
                self.officer3_data,
            ],
            "columns_mapping": {
                column: self.header.index(column) for column in self.header
            },
        }

        officer_importer.data_reconciliation = MockDataReconciliation(processed_data)

        result = officer_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == OfficerImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert not import_log.commit_hash
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 3
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Officer.objects.count() == 5

        check_columns = officer_importer.column_mappings.copy()

        officers_data = [
            self.officer1_data,
            self.officer2_data,
            self.officer3_data,
            self.officer4_data,
            self.officer5_data,
        ]

        for officer_data in officers_data:
            officer = Officer.objects.filter(
                uid=officer_data[check_columns["uid"]]
            ).first()
            assert officer
            field_attrs = [
                "last_name",
                "middle_name",
                "first_name",
                "race",
                "sex",
            ]
            integer_field_attrs = [
                "birth_year",
                "birth_month",
                "birth_day",
            ]

            for attr in field_attrs:
                assert getattr(officer, attr) == (
                    officer_data[check_columns[attr]]
                    if officer_data[check_columns[attr]]
                    else None
                )

            for attr in integer_field_attrs:
                assert getattr(officer, attr) == (
                    int(officer_data[check_columns[attr]])
                    if officer_data[check_columns[attr]]
                    else None
                )

        assert result
        updated_officers = set(
            Officer.objects.filter(is_name_changed=True).values_list("uid", flat=True)
        )
        expected_uids = ["uid_2", "uid_3"]
        assert updated_officers == set(expected_uids)

    def test_delete_not_exist_officer(self):
        officer_importer = OfficerImporter("csv_file_path")

        processed_data = {
            "added_rows": [],
            "deleted_rows": [
                self.officer6_data,
            ],
            "updated_rows": [],
            "columns_mapping": {
                column: self.header.index(column) for column in self.header
            },
        }

        officer_importer.data_reconciliation = MockDataReconciliation(processed_data)

        result = officer_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == OfficerImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert not import_log.commit_hash
        assert import_log.created_rows == 0
        assert import_log.updated_rows == 0
        assert import_log.deleted_rows == 0
        assert not import_log.error_message
        assert import_log.finished_at
