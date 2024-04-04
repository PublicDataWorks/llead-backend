from django.test.testcases import TestCase

from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.models import ImportLog
from data.services import UofImporter
from data.tests.services.util import MockDataReconciliation
from departments.factories import DepartmentFactory
from officers.factories import OfficerFactory
from use_of_forces.factories import UseOfForceFactory
from use_of_forces.models import UseOfForce


class UofImporterTestCase(TestCase):
    def setUp(self):
        uof_1 = UseOfForceFactory(
            uof_uid="uof_uid_1", uid="officer_uid_1", agency="new-orleans-pd"
        )
        uof_2 = UseOfForceFactory(
            uof_uid="uof_uid_2", uid="officer_uid_2", agency="new-orleans-pd"
        )
        uof_3 = UseOfForceFactory(
            uof_uid="uof_uid_3", uid="officer_uid_3", agency="baton-rouge-pd"
        )
        uof_4 = UseOfForceFactory(
            uof_uid="uof_uid_4", uid="officer_uid_4", agency="new-orleans-pd"
        )
        uof_5 = UseOfForceFactory(
            uof_uid="uof_uid_5", uid="officer_uid_5", agency="baton-rouge-pd"
        )

        self.header = list(
            {field.name for field in UseOfForce._meta.fields}
            - UseOfForce.BASE_FIELDS
            - UseOfForce.CUSTOM_FIELDS
        )

        self.uof1_data = [getattr(uof_1, field) for field in self.header]
        self.uof2_data = [getattr(uof_2, field) for field in self.header]
        self.uof3_data = [getattr(uof_3, field) for field in self.header]
        self.uof4_data = [getattr(uof_4, field) for field in self.header]
        self.uof5_data = [getattr(uof_5, field) for field in self.header]

        self.uof5_dup_data = self.uof5_data.copy()

        self.uofs_data = [
            self.uof1_data,
            self.uof2_data,
            self.uof3_data,
            self.uof4_data,
            self.uof5_data,
            self.uof5_dup_data,
        ]

        UseOfForce.objects.all().delete()

    def test_process_successfully(self):
        UseOfForceFactory(uof_uid="uof_uid_1")
        UseOfForceFactory(uof_uid="uof_uid_2")
        UseOfForceFactory(uof_uid="uof_uid_3")

        department_1 = DepartmentFactory(agency_name="New Orleans PD")
        department_2 = DepartmentFactory(agency_name="Baton Rouge PD")

        officer_1 = OfficerFactory(uid="officer_uid_1")
        officer_2 = OfficerFactory(uid="officer_uid_2")
        OfficerFactory(uid="officer_uid_3")
        officer_4 = OfficerFactory(uid="officer_uid_4")
        officer_5 = OfficerFactory(uid="officer_uid_5")

        assert UseOfForce.objects.count() == 3

        uof_importer = UofImporter("csv_file_path")

        processed_data = {
            "added_rows": [self.uof4_data, self.uof5_data, self.uof5_dup_data],
            "deleted_rows": [
                self.uof3_data,
            ],
            "updated_rows": [
                self.uof1_data,
                self.uof2_data,
            ],
            "columns_mapping": {
                column: self.header.index(column) for column in self.header
            },
        }

        uof_importer.data_reconciliation = MockDataReconciliation(processed_data)

        result = uof_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == UofImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert not import_log.commit_hash
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 2
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert UseOfForce.objects.count() == 4

        check_columns = self.header + ["department_id", "officer_id"]
        check_columns_mappings = {
            column: check_columns.index(column) for column in check_columns
        }

        expected_uof1_data = self.uof1_data.copy()
        expected_uof1_data.append(department_1.id)
        expected_uof1_data.append(officer_1.id)

        expected_uof2_data = self.uof2_data.copy()
        expected_uof2_data.append(department_1.id)
        expected_uof2_data.append(officer_2.id)

        expected_uof4_data = self.uof4_data.copy()
        expected_uof4_data.append(department_1.id)
        expected_uof4_data.append(officer_4.id)

        expected_uof5_data = self.uof5_data.copy()
        expected_uof5_data.append(department_2.id)
        expected_uof5_data.append(officer_5.id)

        expected_uofs_data = [
            expected_uof1_data,
            expected_uof2_data,
            expected_uof4_data,
            expected_uof5_data,
        ]

        for uof_data in expected_uofs_data:
            uof = UseOfForce.objects.filter(
                uof_uid=uof_data[check_columns_mappings["uof_uid"]]
            ).first()

            assert uof

            field_attrs = check_columns

            for attr in field_attrs:
                assert getattr(uof, attr) == (
                    uof_data[check_columns_mappings[attr]]
                    if uof_data[check_columns_mappings[attr]]
                    else None
                )

    def test_delete_non_existed_uof(self):
        uof_importer = UofImporter("csv_file_path")

        processed_data = {
            "added_rows": [],
            "deleted_rows": [
                self.uof3_data,
            ],
            "updated_rows": [],
            "columns_mapping": {
                column: self.header.index(column) for column in self.header
            },
        }

        uof_importer.data_reconciliation = MockDataReconciliation(processed_data)

        result = uof_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == UofImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert not import_log.commit_hash
        assert import_log.created_rows == 0
        assert import_log.updated_rows == 0
        assert import_log.deleted_rows == 0
        assert not import_log.error_message
        assert import_log.finished_at
