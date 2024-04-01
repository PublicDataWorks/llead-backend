from abc import ABC, abstractmethod

from django.test import TestCase

from brady.factories.brady_factory import BradyFactory
from brady.models.brady import Brady
from data.services.data_reconciliation import DataReconciliation


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

        output = self.data_reconciliation.reconcile_data()

        assert output == {
            "added_rows": self.csv_data,
            "deleted_rows": [
                [getattr(existed_instance, field) for field in self.fields]
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
