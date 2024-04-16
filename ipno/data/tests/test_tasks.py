from django.test import TestCase

from mock import patch

from data.constants import IMPORT_TASK_ID_CACHE_KEY
from data.tasks import import_data


class ImportDataTaskTestCase(TestCase):
    @patch("data.tasks.cache")
    @patch("data.tasks.DataImporter")
    def test_import_data_task_call_data_importer_service(
        self, mock_data_importer, mock_cache
    ):
        import_data("test_folder")

        mock_data_importer.assert_called_once()
        mock_data_importer.return_value.execute.assert_called_once_with("test_folder")
        mock_cache.delete.assert_called_once_with(IMPORT_TASK_ID_CACHE_KEY)

    @patch("data.tasks.cache")
    @patch("data.tasks.DataImporter")
    def test_import_data_task_delete_cache_even_when_the_task_failed(
        self, mock_data_importer, mock_cache
    ):
        mock_data_importer.return_value.execute.side_effect = Exception()

        with self.assertRaises(Exception):
            import_data("test_folder")

        mock_data_importer.assert_called_once()
        mock_data_importer.return_value.execute.assert_called_once_with("test_folder")
        mock_cache.delete.assert_called_once_with(IMPORT_TASK_ID_CACHE_KEY)
