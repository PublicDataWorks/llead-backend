from django.test import TestCase

from mock import patch

from appeals.models import Appeal
from brady.models import Brady
from citizens.models import Citizen
from complaints.models import Complaint
from data.services.schema_validation import SchemaValidation
from departments.models import Department
from documents.models import Document
from ipno.data.constants import AGENCY_MODEL_NAME
from news_articles.models import NewsArticleClassification
from officers.models import Event, Officer
from people.models import Person
from post_officer_history.models import PostOfficerHistory
from use_of_forces.models import UseOfForce
from utils.models import APITemplateModel


class SchemaTasksTestCase(TestCase):
    def setUp(self):
        self.schema_validation = SchemaValidation()
        self.csv_file_path = "./ipno/data/tests/services/test_data/data_agency.csv"

    def test_get_schemas(self):
        base_fields = APITemplateModel.BASE_FIELDS

        document_fixed_fields = (
            {field.name for field in Document._meta.fields}
            - base_fields
            - Document.CUSTOM_FIELDS
        )
        department_fixed_fields = (
            {field.name for field in Department._meta.fields}
            - base_fields
            - Department.CUSTOM_FIELDS
        )
        event_fixed_fields = (
            {field.name for field in Event._meta.fields}
            - base_fields
            - Event.CUSTOM_FIELDS
        )
        officer_fixed_fields = (
            {field.name for field in Officer._meta.fields}
            - base_fields
            - Officer.CUSTOM_FIELDS
        )
        complaint_fixed_fields = (
            {field.name for field in Complaint._meta.fields}
            - base_fields
            - Complaint.CUSTOM_FIELDS
        )
        useofforce_fixed_fields = (
            {field.name for field in UseOfForce._meta.fields}
            - base_fields
            - UseOfForce.CUSTOM_FIELDS
        )
        person_fixed_fields = (
            {field.name for field in Person._meta.fields}
            - base_fields
            - Person.CUSTOM_FIELDS
        )
        appeal_fixed_fields = (
            {field.name for field in Appeal._meta.fields}
            - base_fields
            - Appeal.CUSTOM_FIELDS
        )
        citizen_fixed_fields = (
            {field.name for field in Citizen._meta.fields}
            - base_fields
            - Citizen.CUSTOM_FIELDS
        )
        brady_fixed_fields = (
            {field.name for field in Brady._meta.fields}
            - base_fields
            - Brady.CUSTOM_FIELDS
        )
        article_classification_fixed_fields = (
            {field.name for field in NewsArticleClassification._meta.fields}
            - base_fields
            - NewsArticleClassification.CUSTOM_FIELDS
        )
        post_officer_history_fixed_fields = (
            {field.name for field in PostOfficerHistory._meta.fields}
            - base_fields
            - PostOfficerHistory.CUSTOM_FIELDS
        )

        expected_schemas = {
            "document": document_fixed_fields,
            "department": department_fixed_fields,
            "event": event_fixed_fields,
            "officer": officer_fixed_fields,
            "complaint": complaint_fixed_fields,
            "useofforce": useofforce_fixed_fields,
            "person": person_fixed_fields,
            "appeal": appeal_fixed_fields,
            "citizen": citizen_fixed_fields,
            "brady": brady_fixed_fields,
            "newsarticleclassification": article_classification_fixed_fields,
            "postofficerhistory": post_officer_history_fixed_fields,
        }

        result = self.schema_validation._get_schemas()

        assert result == expected_schemas

    def test_check_fields(self):
        fixed_fields = {"location", "agency_slug", "agency_name", "unused_field"}
        result = self.schema_validation._check_fields(self.csv_file_path, fixed_fields)

        assert result == ({"unused_field"}, set())

    @patch("data.services.schema_validation.notify_slack")
    @patch("data.services.schema_validation.SchemaValidation._check_fields")
    def test_validate_schemas_success(self, mock_check_fields, mock_notify_slack):
        mock_check_fields.return_value = set(), set()
        self.schema_validation.models = [Department]
        data_mapping = {AGENCY_MODEL_NAME: "csv_file_path"}
        self.schema_validation.validate_schemas(data_mapping)

        expected_message = (
            "====================\nResult after schema validation in *`TEST`*"
            " environment,\n\n*Required fields are validated successfully!*\n\n"
        )
        mock_notify_slack.assert_called_with(expected_message)

    @patch("data.services.schema_validation.notify_slack")
    @patch("data.services.schema_validation.SchemaValidation._check_fields")
    def test_validate_schemas_error(self, mock_check_fields, mock_notify_slack):
        mock_check_fields.return_value = {"missing_field"}, set()
        self.schema_validation.models = [Department]
        data_mapping = {AGENCY_MODEL_NAME: "csv_file_path"}
        self.schema_validation.validate_schemas(data_mapping)

        expected_message = (
            "====================\nResult after schema validation in *`TEST`*"
            " environment,\n\n*ERROR happened*\n\n>- Missing required fields in table"
            " `department`: *missing_field*\n"
        )
        mock_notify_slack.assert_called_with(expected_message)

    @patch("data.services.schema_validation.notify_slack")
    @patch("data.services.schema_validation.SchemaValidation._check_fields")
    def test_validate_schemas_unused_fields(self, mock_check_fields, mock_notify_slack):
        mock_check_fields.return_value = set(), {"unused_field"}
        self.schema_validation.models = [Department]
        data_mapping = {AGENCY_MODEL_NAME: "csv_file_path"}
        self.schema_validation.validate_schemas(data_mapping)

        expected_message = (
            "====================\nResult after schema validation in *`TEST`*"
            " environment,\n\n*Required fields are validated"
            " successfully!*\n\n\n_*(Warning) Unused fields:*_\n\n>- Unused fields in"
            " table `department`: unused_field\n"
        )
        mock_notify_slack.assert_called_with(expected_message)
