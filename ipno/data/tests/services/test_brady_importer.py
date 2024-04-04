from django.test.testcases import TestCase

from brady.factories.brady_factory import BradyFactory
from brady.models import Brady
from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.models import ImportLog
from data.services import BradyImporter
from data.tests.services.util import MockDataReconciliation
from departments.factories import DepartmentFactory
from officers.factories import OfficerFactory


class BradyImporterTestCase(TestCase):
    def setUp(self):
        brady_1 = BradyFactory(
            brady_uid="brady-uid1",
            uid="officer-uid1",
            agency="new-orleans-pd",
        )
        brady_2 = BradyFactory(
            brady_uid="brady-uid2",
            uid="officer-uid2",
            agency="new-orleans-pd",
        )
        brady_3 = BradyFactory(
            brady_uid="brady-uid3", uid="officer-uid2", agency="baton-rouge-pd"
        )
        brady_4 = BradyFactory(
            brady_uid="brady-uid4",
            uid="officer-uid3",
            agency="new-orleans-pd",
        )
        brady_5 = BradyFactory(
            brady_uid="brady-uid5",
            uid="officer-uid3",
            agency="baton-rouge-pd",
        )
        brady_6 = BradyFactory(
            brady_uid="brady-uid6",
            uid="officer-uid2",
            agency="baton-rouge-pd",
        )

        self.header = list(
            {field.name for field in Brady._meta.fields}
            - Brady.BASE_FIELDS
            - Brady.CUSTOM_FIELDS
        )
        self.brady1_data = [getattr(brady_1, field) for field in self.header]
        self.brady2_data = [getattr(brady_2, field) for field in self.header]
        self.brady3_data = [getattr(brady_3, field) for field in self.header]
        self.brady4_data = [getattr(brady_4, field) for field in self.header]
        self.brady5_data = [getattr(brady_5, field) for field in self.header]
        self.brady6_data = [getattr(brady_6, field) for field in self.header]
        self.brady5_dup_data = self.brady5_data.copy()

        Brady.objects.all().delete()

    def test_process_successfully(self):
        BradyFactory(brady_uid="brady-uid1")
        BradyFactory(brady_uid="brady-uid2")
        BradyFactory(brady_uid="brady-uid3")
        BradyFactory(brady_uid="brady-uid6")

        department_1 = DepartmentFactory(agency_name="New Orleans PD")
        department_2 = DepartmentFactory(agency_name="Baton Rouge PD")

        officer_1 = OfficerFactory(uid="officer-uid1")
        officer_2 = OfficerFactory(uid="officer-uid2")
        officer_3 = OfficerFactory(uid="officer-uid3")

        assert Brady.objects.count() == 4

        brady_importer = BradyImporter("csv_file_path")

        processed_data = {
            "added_rows": [self.brady4_data, self.brady5_data],
            "deleted_rows": [
                self.brady3_data,
            ],
            "updated_rows": [
                self.brady1_data,
                self.brady2_data,
                self.brady6_data,
            ],
            "columns_mapping": {
                column: self.header.index(column) for column in self.header
            },
        }

        brady_importer.data_reconciliation = MockDataReconciliation(processed_data)

        result = brady_importer.process()

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == brady_importer.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert not import_log.commit_hash
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 3
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Brady.objects.count() == 5

        assert result

        check_columns = self.header + ["department_id", "officer_id"]
        check_columns_mappings = {
            column: check_columns.index(column) for column in check_columns
        }

        expected_brady1_data = self.brady1_data.copy()
        expected_brady1_data.append(department_1.id)
        expected_brady1_data.append(officer_1.id)

        expected_brady2_data = self.brady2_data.copy()
        expected_brady2_data.append(department_1.id)
        expected_brady2_data.append(officer_2.id)

        expected_brady4_data = self.brady4_data.copy()
        expected_brady4_data.append(department_1.id)
        expected_brady4_data.append(officer_3.id)

        expected_brady5_data = self.brady5_data.copy()
        expected_brady5_data.append(department_2.id)
        expected_brady5_data.append(officer_3.id)

        expected_brady6_data = self.brady6_data.copy()
        expected_brady6_data.append(department_2.id)
        expected_brady6_data.append(officer_2.id)

        expected_brady_data = [
            expected_brady1_data,
            expected_brady2_data,
            expected_brady4_data,
            expected_brady5_data,
            expected_brady6_data,
        ]

        for brady_data in expected_brady_data:
            brady = Brady.objects.filter(
                brady_uid=brady_data[check_columns_mappings["brady_uid"]]
                if brady_data[check_columns_mappings["brady_uid"]]
                else None
            ).first()

            assert brady
            field_attrs = self.header

            for attr in field_attrs:
                assert getattr(brady, attr) == (
                    brady_data[check_columns_mappings[attr]]
                    if brady_data[check_columns_mappings[attr]]
                    else None
                )

            assert (
                brady.department.id
                == brady_data[check_columns_mappings["department_id"]]
            )
            assert brady.officer.id == brady_data[check_columns_mappings["officer_id"]]

    def test_delete_not_exist_brady(self):
        brady_importer = BradyImporter("csv_file_path")

        processed_data = {
            "added_rows": [],
            "deleted_rows": [
                self.brady1_data,
            ],
            "updated_rows": [],
            "columns_mapping": {
                column: self.header.index(column) for column in self.header
            },
        }

        brady_importer.data_reconciliation = MockDataReconciliation(processed_data)

        result = brady_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == brady_importer.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert not import_log.commit_hash
        assert import_log.created_rows == 0
        assert import_log.updated_rows == 0
        assert import_log.deleted_rows == 0
        assert not import_log.error_message
        assert import_log.finished_at
