from django.core.management import call_command
from django.test import TestCase

from mock import Mock, patch


class ImportDataCommandTestCase(TestCase):
    @patch("data.services.data_importer.DataImporter")
    def test_call_command(self, mock_data_importer):
        mock_data_importer.return_value.execute = Mock()

        call_command("import_data", "folder_name")

        mock_data_importer.return_value.execute.assert_called_with("folder_name")
