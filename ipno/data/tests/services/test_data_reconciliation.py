import csv
from abc import ABC, abstractmethod

from django.test import TestCase

from appeals.factories.appeal_factory import AppealFactory
from appeals.models.appeal import Appeal
from brady.factories.brady_factory import BradyFactory
from brady.models.brady import Brady
from citizens.factory.citizen_factory import CitizenFactory
from citizens.models.citizen import Citizen
from complaints.factories.complaint_factory import ComplaintFactory
from complaints.models.complaint import Complaint
from data.constants import (
    AGENCY_MODEL_NAME,
    APPEAL_MODEL_NAME,
    BRADY_MODEL_NAME,
    CITIZEN_MODEL_NAME,
    COMPLAINT_MODEL_NAME,
    DOCUMENT_MODEL_NAME,
    EVENT_MODEL_NAME,
    NEWS_ARTICLE_CLASSIFICATION_MODEL_NAME,
    OFFICER_MODEL_NAME,
    PERSON_MODEL_NAME,
    POST_OFFICE_HISTORY_MODEL_NAME,
    USE_OF_FORCE_MODEL_NAME,
)
from data.services.data_reconciliation import DataReconciliation
from departments.factories.department_factory import DepartmentFactory
from departments.models.department import Department
from documents.factories.document_factory import DocumentFactory
from documents.models.document import Document
from news_articles.factories.news_article_classification_factory import (
    NewsArticleClassificationFactory,
)
from news_articles.models.news_article_classification import NewsArticleClassification
from officers.factories.event_factory import EventFactory
from officers.factories.officer_factory import OfficerFactory
from officers.models.event import Event
from officers.models.officer import Officer
from people.factories.person_factory import PersonFactory
from people.models.person import Person
from post_officer_history.factories.post_officer_history_factory import (
    PostOfficerHistoryFactory,
)
from post_officer_history.models.post_officer_history import PostOfficerHistory
from use_of_forces.factories.use_of_force_factory import UseOfForceFactory
from use_of_forces.models.use_of_force import UseOfForce


class DataReconciliationTestCaseBase(ABC):
    def setUp(self):
        self.prepare_data()
        self._prepare_csv_data()

    @abstractmethod
    def prepare_data(self):
        pass

    @abstractmethod
    def create_db_instance(self, id):
        pass

    def _prepare_csv_data(self):
        with open(self.csv_file_path) as csvfile:
            reader = csv.reader(
                csvfile,
                strict=True,
            )

            reader_list = list(reader)
            headers = reader_list[0]
            # FIXME: Ideally, we don't need to store this
            self.content = reader_list[1:]  # Skip the header row

        included_idx = [headers.index(i) for i in self.fields]

        self.csv_data = []
        self.index_column = headers.index(self.index_column_name) or 0

        for c in self.content:
            self.csv_data.append([str(c[i]) for i in included_idx])

    def test_detect_added_rows_sucessfully(self):
        output = self.data_reconciliation.reconcile_data()

        assert output == {
            "added_rows": self.csv_data,
            "deleted_rows": [],
            "updated_rows": [],
            "columns_mapping": {
                column: self.fields.index(column) for column in self.fields
            },
        }

    def test_detect_deleted_rows_sucessfully(self):
        existed_instance = self.Factory()
        existed_instance.refresh_from_db()

        output = self.data_reconciliation.reconcile_data()

        assert output == {
            "added_rows": self.csv_data,
            "deleted_rows": [
                [str(getattr(existed_instance, field) or "") for field in self.fields]
            ],
            "updated_rows": [],
            "columns_mapping": {
                column: self.fields.index(column) for column in self.fields
            },
        }

    def test_detect_updated_rows_successfully(self):
        self.create_db_instance(self.content[0][self.index_column])

        output = self.data_reconciliation.reconcile_data()

        assert output == {
            "added_rows": self.csv_data[1:],
            "deleted_rows": [],
            "updated_rows": [self.csv_data[0]],
            "columns_mapping": {
                column: self.fields.index(column) for column in self.fields
            },
        }


class BradyDataReconciliationTestCase(DataReconciliationTestCaseBase, TestCase):
    def prepare_data(self):
        self.csv_file_path = "./ipno/data/tests/services/test_data/data_brady.csv"
        self.fields = [
            field.name
            for field in Brady._meta.fields
            if field.name not in Brady.BASE_FIELDS
            and field.name not in Brady.CUSTOM_FIELDS
        ]
        self.data_reconciliation = DataReconciliation(
            BRADY_MODEL_NAME, self.csv_file_path
        )
        self.Factory = BradyFactory
        self.index_column_name = "brady_uid"

    def create_db_instance(self, id):
        return self.Factory.create(
            brady_uid=id,
        )


class AgencyDataReconciliationTestCase(DataReconciliationTestCaseBase, TestCase):
    def prepare_data(self):
        self.csv_file_path = "./ipno/data/tests/services/test_data/data_agency.csv"
        self.fields = [
            field.name
            for field in Department._meta.fields
            if field.name not in Department.BASE_FIELDS
            and field.name not in Department.CUSTOM_FIELDS
        ]
        self.data_reconciliation = DataReconciliation(
            AGENCY_MODEL_NAME, self.csv_file_path
        )
        self.Factory = DepartmentFactory
        self.index_column_name = "agency_slug"

    def create_db_instance(self, id):
        return self.Factory.create(agency_slug=id)


class OfficerDataReconciliationTestCase(DataReconciliationTestCaseBase, TestCase):
    def prepare_data(self):
        self.csv_file_path = "./ipno/data/tests/services/test_data/data_personnel.csv"
        self.fields = [
            field.name
            for field in Officer._meta.fields
            if field.name not in Officer.BASE_FIELDS
            and field.name not in Officer.CUSTOM_FIELDS
        ]
        self.data_reconciliation = DataReconciliation(
            OFFICER_MODEL_NAME, self.csv_file_path
        )
        self.Factory = OfficerFactory
        self.index_column_name = "uid"

    def create_db_instance(self, id):
        return self.Factory.create(uid=id)


class ArticleClassificationDataReconciliationTestCase(
    DataReconciliationTestCaseBase, TestCase
):
    def prepare_data(self):
        self.csv_file_path = (
            "./ipno/data/tests/services/test_data/data_news_article_classification.csv"
        )
        self.fields = [
            field.name
            for field in NewsArticleClassification._meta.fields
            if field.name not in NewsArticleClassification.BASE_FIELDS
            and field.name not in NewsArticleClassification.CUSTOM_FIELDS
        ]
        self.data_reconciliation = DataReconciliation(
            NEWS_ARTICLE_CLASSIFICATION_MODEL_NAME, self.csv_file_path
        )
        self.Factory = NewsArticleClassificationFactory
        self.index_column_name = "article_id"

    def create_db_instance(self, id):
        return self.Factory.create(article_id=id)


class AllegationDataReconciliationTestCase(DataReconciliationTestCaseBase, TestCase):
    def prepare_data(self):
        self.csv_file_path = "./ipno/data/tests/services/test_data/data_allegation.csv"
        self.fields = [
            field.name
            for field in Complaint._meta.fields
            if field.name not in Complaint.BASE_FIELDS
            and field.name not in Complaint.CUSTOM_FIELDS
        ]
        self.data_reconciliation = DataReconciliation(
            COMPLAINT_MODEL_NAME, self.csv_file_path
        )
        self.Factory = ComplaintFactory
        self.index_column_name = "allegation_uid"

    def create_db_instance(self, id):
        return self.Factory.create(allegation_uid=id)


class UseOfForceDataReconciliationTestCase(DataReconciliationTestCaseBase, TestCase):
    def prepare_data(self):
        self.csv_file_path = (
            "./ipno/data/tests/services/test_data/data_use_of_force.csv"
        )
        self.fields = [
            field.name
            for field in UseOfForce._meta.fields
            if field.name not in UseOfForce.BASE_FIELDS
            and field.name not in UseOfForce.CUSTOM_FIELDS
        ]
        self.data_reconciliation = DataReconciliation(
            USE_OF_FORCE_MODEL_NAME, self.csv_file_path
        )
        self.Factory = UseOfForceFactory
        self.index_column_name = "uof_uid"

    def create_db_instance(self, id):
        return self.Factory.create(uof_uid=id)


class CitizenDataReconciliationTestCase(DataReconciliationTestCaseBase, TestCase):
    def prepare_data(self):
        self.csv_file_path = "./ipno/data/tests/services/test_data/data_citizen.csv"
        self.fields = [
            field.name
            for field in Citizen._meta.fields
            if field.name not in Citizen.BASE_FIELDS
            and field.name not in Citizen.CUSTOM_FIELDS
        ]
        self.data_reconciliation = DataReconciliation(
            CITIZEN_MODEL_NAME, self.csv_file_path
        )
        self.Factory = CitizenFactory
        self.index_column_name = "citizen_uid"

    def create_db_instance(self, id):
        return self.Factory.create(citizen_uid=id)


class AppealDataReconciliationTestCase(DataReconciliationTestCaseBase, TestCase):
    def prepare_data(self):
        self.csv_file_path = "./ipno/data/tests/services/test_data/data_appeal.csv"
        self.fields = [
            field.name
            for field in Appeal._meta.fields
            if field.name not in Appeal.BASE_FIELDS
            and field.name not in Appeal.CUSTOM_FIELDS
        ]
        self.data_reconciliation = DataReconciliation(
            APPEAL_MODEL_NAME, self.csv_file_path
        )
        self.Factory = AppealFactory
        self.index_column_name = "appeal_uid"

    def create_db_instance(self, id):
        return self.Factory.create(appeal_uid=id)


class EventDataReconciliationTestCase(DataReconciliationTestCaseBase, TestCase):
    def prepare_data(self):
        self.csv_file_path = "./ipno/data/tests/services/test_data/data_event.csv"
        self.fields = [
            field.name
            for field in Event._meta.fields
            if field.name not in Event.BASE_FIELDS
            and field.name not in Event.CUSTOM_FIELDS
        ]
        self.data_reconciliation = DataReconciliation(
            EVENT_MODEL_NAME, self.csv_file_path
        )
        self.Factory = EventFactory
        self.index_column_name = "event_uid"

    def create_db_instance(self, id):
        return self.Factory.create(event_uid=id)


class PostOfficerHistoryDataReconciliationTestCase(
    DataReconciliationTestCaseBase, TestCase
):
    def prepare_data(self):
        self.csv_file_path = (
            "./ipno/data/tests/services/test_data/data_post_officer_history.csv"
        )
        self.fields = [
            field.name
            for field in PostOfficerHistory._meta.fields
            if field.name not in PostOfficerHistory.BASE_FIELDS
            and field.name not in PostOfficerHistory.CUSTOM_FIELDS
        ]
        self.data_reconciliation = DataReconciliation(
            POST_OFFICE_HISTORY_MODEL_NAME, self.csv_file_path
        )
        self.Factory = PostOfficerHistoryFactory
        self.index_column_name = "uid"

    def create_db_instance(self, id):
        return self.Factory.create(uid=id)


class PersonDataReconciliationTestCase(DataReconciliationTestCaseBase, TestCase):
    def prepare_data(self):
        self.csv_file_path = "./ipno/data/tests/services/test_data/data_person.csv"
        self.fields = [
            field.name
            for field in Person._meta.fields
            if field.name not in Person.BASE_FIELDS
            and field.name not in Person.CUSTOM_FIELDS
        ]
        self.data_reconciliation = DataReconciliation(
            PERSON_MODEL_NAME, self.csv_file_path
        )
        self.Factory = PersonFactory
        self.index_column_name = "person_id"

    def create_db_instance(self, id):
        return self.Factory.create(person_id=id)


class DocumentDataReconciliationTestCase(TestCase):
    def setUp(self):
        self.prepare_data()
        self._prepare_csv_data()

    def prepare_data(self):
        self.csv_file_path = "./ipno/data/tests/services/test_data/data_document.csv"
        self.fields = [
            field.name
            for field in Document._meta.fields
            if field.name not in Document.BASE_FIELDS
            and field.name not in Document.CUSTOM_FIELDS
        ]
        self.fields += ["page_count"]
        self.data_reconciliation = DataReconciliation(
            DOCUMENT_MODEL_NAME, self.csv_file_path
        )
        self.Factory = DocumentFactory
        self.index_column_names = ["docid", "hrg_no", "matched_uid", "agency"]

    def _prepare_csv_data(self):
        with open(self.csv_file_path) as csvfile:
            reader = csv.reader(
                csvfile,
                strict=True,
            )

            reader_list = list(reader)
            headers = reader_list[0]
            self.content = reader_list[1:]  # Skip the header row

        included_idx = [headers.index(i) for i in self.fields]
        self.index_columns = [headers.index(i) for i in self.index_column_names]
        self.csv_data = []

        for c in self.content:
            self.csv_data.append([str(c[i]) for i in included_idx])

    def test_detect_added_rows_sucessfully(self):
        output = self.data_reconciliation.reconcile_data()

        assert output == {
            "added_rows": self.csv_data,
            "deleted_rows": [],
            "updated_rows": [],
            "columns_mapping": {
                column: self.fields.index(column) for column in self.fields
            },
        }

    def test_detect_deleted_rows_sucessfully(self):
        existed_instance = self.Factory()
        existed_instance.refresh_from_db()

        output = self.data_reconciliation.reconcile_data()

        assert output == {
            "added_rows": self.csv_data,
            # page_count should be included in the result, as a empty string,
            # this does not matter in the case of delete since we only care for the id,
            # but we keep it all for the backward compatibility with WRGL.
            "deleted_rows": [
                [
                    str(getattr(existed_instance, field) or "")
                    for field in self.fields
                    if field != "page_count"
                ]
                + [""]
            ],
            "updated_rows": [],
            "columns_mapping": {
                column: self.fields.index(column) for column in self.fields
            },
        }

    def test_detect_updated_rows_successfully(self):
        self.Factory(
            docid=self.content[0][self.index_columns[0]],
            hrg_no=self.content[0][self.index_columns[1]],
            matched_uid=self.content[0][self.index_columns[2]],
            agency=self.content[0][self.index_columns[3]],
        )

        output = self.data_reconciliation.reconcile_data()

        assert output == {
            "added_rows": self.csv_data[1:],
            "deleted_rows": [],
            "updated_rows": [self.csv_data[0]],
            "columns_mapping": {
                column: self.fields.index(column) for column in self.fields
            },
        }

    def test_detect_delete_by_partial_key_correctly(self):
        self.Factory(
            docid=self.content[0][self.index_columns[0]],
            hrg_no=self.content[0][self.index_columns[1]],
            matched_uid=self.content[0][self.index_columns[2]],
            agency=self.content[0][self.index_columns[3]],
        )

        to_deleted = self.Factory(
            docid=self.content[1][self.index_columns[0]],
            hrg_no=self.content[1][self.index_columns[1]],
        )

        output = self.data_reconciliation.reconcile_data()

        assert output == {
            "added_rows": self.csv_data[1:],
            # page_count should be included in the result, as a empty string,
            # this does not matter in the case of delete since we only care for the id,
            # but we keep it all for the backward compatibility with WRGL.
            "deleted_rows": [
                [
                    str(getattr(to_deleted, field) or "")
                    for field in self.fields
                    if field != "page_count"
                ]
                + [""]
            ],
            "updated_rows": [self.csv_data[0]],
            "columns_mapping": {
                column: self.fields.index(column) for column in self.fields
            },
        }
