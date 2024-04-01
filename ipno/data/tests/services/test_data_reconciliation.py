from abc import ABC, abstractmethod

from django.test import TestCase

from brady.factories.brady_factory import BradyFactory
from brady.models.brady import Brady
from data.services.data_reconciliation import DataReconciliation
from departments.factories.department_factory import DepartmentFactory
from departments.models.department import Department
from officers.factories.officer_factory import OfficerFactory
from officers.models.officer import Officer


class DataReconciliationTestCaseBase(ABC):
    @abstractmethod
    def setUp(self):
        pass

    @abstractmethod
    def create_db_instance(self, id):
        pass

    def test_detect_added_rows_sucessfully(self):
        output = self.data_reconciliation.reconcile_data()

        assert output == {
            "added_rows": self.csv_data,
            "deleted_rows": [],
            "updated_rows": [],
        }

    def test_detect_deleted_rows_sucessfully(self):
        existed_instance = self.Factory()
        existed_instance.refresh_from_db()

        output = self.data_reconciliation.reconcile_data()

        assert output == {
            "added_rows": self.csv_data,
            "deleted_rows": [
                [getattr(existed_instance, field) or "" for field in self.fields]
            ],
            "updated_rows": [],
        }

    def test_detect_updated_rows_successfully(self):
        self.create_db_instance(self.csv_data[0][0])

        output = self.data_reconciliation.reconcile_data()

        assert output == {
            "added_rows": self.csv_data[1:],
            "deleted_rows": [],
            "updated_rows": [self.csv_data[0]],
        }


class BradyDataReconciliationTestCase(DataReconciliationTestCaseBase, TestCase):
    def setUp(self):
        self.csv_data = [
            [
                "0673e24f8b24bd667957bf5e1026ee75",
                "69da9ded5689b16b67336521d1b73de8",
                "sustained",
                "resigned",
                "finding of untruthfulness",
                "",
                "east-baton-rouge-da",
                "",
                "east-baton-rouge-so",
            ],
            [
                "0c43cc3e65dde58a255dd3e51ab6d375",
                "9d87622c956cfc134df54871fd6b61a8",
                "arrested and/or convicted",
                "resigned",
                "criminal violation",
                "",
                "east-baton-rouge-da",
                "",
                "baton-rouge-pd",
            ],
            [
                "0d82a1ee62391d6e7be30f6e7aaf813a",
                "f5adc47d9ca7b64c79998d630cbf228a",
                "arrested and/or convicted",
                "",
                "criminal violation",
                "",
                "east-baton-rouge-da",
                "",
                "baton-rouge-pd",
            ],
            [
                "10f0182961bd53aa9dfe9f2fd099cc7e",
                "a523e2dbbe70123869479e34614081c4",
                "",
                "",
                (
                    "internal investigation in late 2014 as to why his police car was"
                    " found neglected and"
                ),
                "",
                "east-baton-rouge-da",
                "",
                "baton-rouge-pd",
            ],
        ]

        self.fields = [
            field.name
            for field in Brady._meta.fields
            if field.name not in Brady.BASE_FIELDS
            and field.name not in Brady.CUSTOM_FIELDS
        ]

        self.data_reconciliation = DataReconciliation(
            "brady", "./ipno/data/tests/services/test_data/data_brady.csv"
        )

        self.Factory = BradyFactory

    def create_db_instance(self, id):
        return self.Factory.create(
            brady_uid=id,
        )


class AgencyDataReconciliationTestCase(DataReconciliationTestCaseBase, TestCase):
    def setUp(self):
        self.csv_data = [
            [
                "29th-judicial-district-court-da",
                "29th Judicial District Court District Attorney's Office",
                "30.9842977, -91.9623327",
            ],
            ["2nd-da", "2nd District Attorney's Office", "30.9842977, -91.9623327"],
            [
                "east-baton-rouge-da",
                "East Baton Rouge District Attorney's Office",
                "30.4459984, -91.1879553",
            ],
            [
                "webster-coroners-office",
                "Webster Coroners Office",
                "32.6138621, -93.2889402",
            ],
        ]

        self.fields = [
            field.name
            for field in Department._meta.fields
            if field.name not in Department.BASE_FIELDS
            and field.name not in Department.CUSTOM_FIELDS
        ]

        self.data_reconciliation = DataReconciliation(
            "department", "./ipno/data/tests/services/test_data/data_agency.csv"
        )

        self.Factory = DepartmentFactory

    def create_db_instance(self, id):
        return self.Factory.create(agency_slug=id)


class OfficerDataReconciliationTestCase(DataReconciliationTestCaseBase, TestCase):
    def setUp(self):
        self.csv_data = [
            [
                "0001fecd10206530e6dc7891eb1848f1",
                "Matey",
                "L",
                "Melissa",
                "",
                "",
                "",
                "",
                "",
                "new-orleans-harbor-pd",
            ],
            [
                "0004c9b5caefdae69b2908a773c15425",
                "Bell",
                "",
                "Damon",
                "",
                "",
                "",
                "",
                "",
                "tulane-university-pd",
            ],
            [
                "00060e9b48e51424bc0d2e06da389186",
                "Allen",
                "A",
                "Kirk",
                "1959.0",
                "",
                "",
                "Black",
                "Male",
                "new-orleans-pd",
            ],
            [
                "000d203f126752c445440a3b1e8c280c",
                "Gongre ",
                "L",
                "Rick",
                "1953.0",
                "",
                "",
                "",
                "",
                "plaquemines-so",
            ],
            [
                "000dbb5607763c33ef12c61a33e3c7a3",
                "Perriott",
                "",
                "Jonas",
                "1980.0",
                "1.0",
                "31.0",
                "",
                "",
                "new-orleans-pd",
            ],
        ]

        self.fields = [
            field.name
            for field in Officer._meta.fields
            if field.name not in Officer.BASE_FIELDS
            and field.name not in Officer.CUSTOM_FIELDS
        ]

        self.data_reconciliation = DataReconciliation(
            "officer", "./ipno/data/tests/services/test_data/data_personnel.csv"
        )

        self.Factory = OfficerFactory

    def create_db_instance(self, id):
        return self.Factory.create(uid=id)
