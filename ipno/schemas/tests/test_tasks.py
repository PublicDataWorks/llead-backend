from django.test import TestCase

from mock import patch

from appeals.models import Appeal
from brady.models import Brady
from citizens.models import Citizen
from complaints.models import Complaint
from data.factories import WrglRepoFactory
from departments.models import Department
from documents.models import Document
from officers.constants import EVENT_KINDS
from officers.models import Event, Officer
from people.models import Person
from schemas.tasks import check_fields, get_schemas, validate_schemas
from use_of_forces.models import UseOfForce
from utils.models import APITemplateModel


class SchemaTasksTestCase(TestCase):
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
        }

        result = get_schemas()

        for model, fields in result[0].items():
            result[0][model] = set(fields)

        assert result[0] == expected_schemas
        assert list(result[1]["kind"]) == EVENT_KINDS

    @patch("schemas.tasks.requests.get")
    def test_check_fields(self, mock_request_get):
        mock_request_get.return_value.status_code = 200
        mock_request_get.return_value.json.return_value = {
            "table": {"columns": ["name", "slug"]},
            "sum": "test_sum",
        }
        fixed_fields = {"name", "officer"}

        result = check_fields("department", fixed_fields)

        assert result[0] == "test_sum"
        assert result[1] == {"officer"}
        assert result[2] == {"slug"}

    @patch("schemas.tasks.check_fields")
    @patch("schemas.tasks.notify_slack")
    @patch("schemas.tasks.SCHEMA_MAPPING", {"agency-reference-list": "department"})
    def test_validate_schemas_success(self, mock_notify_slack, mock_check_fields):
        mock_check_fields.return_value = ("test_sum", set(), set())

        wrgl_repo = WrglRepoFactory(
            data_model="department",
            repo_name="agency-reference-list",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
            latest_commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
        )

        validate_schemas()
        wrgl_repo.refresh_from_db()

        mock_notify_slack.assert_called_with(
            "====================\nResult after schema validation in *`TEST`*"
            " environment,\n\n*Required fields are validated successfully!*\n\n"
        )
        assert wrgl_repo.latest_commit_hash == "test_sum"

    @patch("schemas.tasks.check_fields")
    @patch("schemas.tasks.notify_slack")
    @patch("schemas.tasks.SCHEMA_MAPPING", {"agency-reference-list": "department"})
    def test_validate_schemas_success_with_unused_fields(
        self, mock_notify_slack, mock_check_fields
    ):
        mock_check_fields.return_value = ("test_sum", set(), {"unused_field"})

        wrgl_repo = WrglRepoFactory(
            data_model="department",
            repo_name="agency-reference-list",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
            latest_commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
        )

        validate_schemas()
        wrgl_repo.refresh_from_db()

        mock_notify_slack.assert_called_with(
            "====================\nResult after schema validation in *`TEST`*"
            " environment,\n\n*Required fields are validated"
            " successfully!*\n\n\n_*(Warning) Unused fields:*_\n\n>- Unused fields in"
            " table `agency-reference-list`: unused_field\n"
        )
        assert wrgl_repo.latest_commit_hash == "test_sum"

    @patch("schemas.tasks.check_fields")
    @patch("schemas.tasks.notify_slack")
    @patch("schemas.tasks.SCHEMA_MAPPING", {"agency-reference-list": "department"})
    def test_validate_schemas_fail(self, mock_notify_slack, mock_check_fields):
        mock_check_fields.return_value = (
            "test_sum",
            {"required_field"},
            set(),
        )

        wrgl_repo = WrglRepoFactory(
            data_model="department",
            repo_name="agency-reference-list",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
            latest_commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
        )

        validate_schemas()
        wrgl_repo.refresh_from_db()

        mock_notify_slack.assert_called_with(
            "====================\nResult after schema validation in *`TEST`*"
            " environment,\n\n*ERROR happened*\n\n>- Missing required fields in table"
            " `agency-reference-list`: *required_field*\n"
        )
        assert wrgl_repo.latest_commit_hash == "bf56dded0b1c4b57f425acb75d48e68c"

    @patch("schemas.tasks.check_fields")
    @patch("schemas.tasks.notify_slack")
    @patch("schemas.tasks.SCHEMA_MAPPING", {"agency-reference-list": "department"})
    def test_validate_schemas_fail_with_unused_fields(
        self, mock_notify_slack, mock_check_fields
    ):
        mock_check_fields.return_value = (
            "test_sum",
            {"required_field"},
            {"unused_field"},
        )

        wrgl_repo = WrglRepoFactory(
            data_model="department",
            repo_name="agency-reference-list",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
            latest_commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
        )

        validate_schemas()
        wrgl_repo.refresh_from_db()

        mock_notify_slack.assert_called_with(
            "====================\nResult after schema validation in *`TEST`*"
            " environment,\n\n*ERROR happened*\n\n>- Missing required fields in table"
            " `agency-reference-list`: *required_field*\n\n_*(Warning) Unused"
            " fields:*_\n\n>- Unused fields in table `agency-reference-list`:"
            " unused_field\n"
        )
        assert wrgl_repo.latest_commit_hash == "bf56dded0b1c4b57f425acb75d48e68c"
