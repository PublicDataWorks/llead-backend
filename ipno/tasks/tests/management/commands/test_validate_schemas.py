from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase


class ValidateSchemasCommandTestCase(TestCase):
    @patch("tasks.management.commands.validate_schemas.validate_schemas")
    def test_handle(self, mock_validate_schemas):
        call_command("validate_schemas")
        mock_validate_schemas.assert_called()
