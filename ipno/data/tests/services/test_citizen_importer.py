from django.test.testcases import TestCase

from citizens.factory import CitizenFactory
from citizens.models import Citizen
from complaints.factories import ComplaintFactory
from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.models import ImportLog
from data.services import CitizenImporter
from data.tests.services.util import MockDataReconciliation
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

        assert Citizen.objects.count() == 3

        citizen_importer = CitizenImporter("csv_file_path")

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
            "columns_mapping": {
                column: self.header.index(column) for column in self.header
            },
        }

        citizen_importer.data_reconciliation = MockDataReconciliation(processed_data)

        result = citizen_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == CitizenImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert not import_log.commit_hash
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 2
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Citizen.objects.count() == 4

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
        citizen_importer = CitizenImporter("csv_file_path")

        processed_data = {
            "added_rows": [],
            "deleted_rows": [
                self.citizen_3_data,
            ],
            "updated_rows": [],
            "columns_mapping": {
                column: self.header.index(column) for column in self.header
            },
        }

        citizen_importer.data_reconciliation = MockDataReconciliation(processed_data)

        result = citizen_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == CitizenImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert not import_log.commit_hash
        assert import_log.created_rows == 0
        assert import_log.updated_rows == 0
        assert import_log.deleted_rows == 0
        assert not import_log.error_message
        assert import_log.finished_at
