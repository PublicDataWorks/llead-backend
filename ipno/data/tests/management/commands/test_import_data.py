from django.core.management import call_command
from django.test import TestCase

from mock import patch


class CreateInitialWRGLReposCommandTestCase(TestCase):
    @patch('utils.search_index.rebuild_search_index')
    @patch('data.services.event_importer.EventImporter.process')
    @patch('data.services.complaint_importer.ComplaintImporter.process')
    @patch('data.services.uof_importer.UofImporter.process')
    @patch('data.services.officer_importer.OfficerImporter.process')
    def test_call_command(
            self,
            officer_process_mock,
            uof_process_mock,
            complaint_process_mock,
            event_process_mock,
            rebuild_search_index_mock,
    ):
        officer_process_mock.return_value = True
        uof_process_mock.return_value = False
        complaint_process_mock.return_value = True
        event_process_mock.return_value = False
        call_command('import_data')

        officer_process_mock.assert_called()
        uof_process_mock.assert_called()
        complaint_process_mock.assert_called()
        event_process_mock.assert_called()
        rebuild_search_index_mock.assert_called()

    @patch('utils.search_index.rebuild_search_index')
    @patch('data.services.event_importer.EventImporter.process')
    @patch('data.services.complaint_importer.ComplaintImporter.process')
    @patch('data.services.uof_importer.UofImporter.process')
    @patch('data.services.officer_importer.OfficerImporter.process')
    def test_call_command_with_no_new_data(
            self,
            officer_process_mock,
            uof_process_mock,
            complaint_process_mock,
            event_process_mock,
            rebuild_search_index_mock,
    ):
        officer_process_mock.return_value = False
        uof_process_mock.return_value = False
        complaint_process_mock.return_value = False
        event_process_mock.return_value = False
        call_command('import_data')

        officer_process_mock.assert_called()
        uof_process_mock.assert_called()
        complaint_process_mock.assert_called()
        event_process_mock.assert_called()
        rebuild_search_index_mock.assert_not_called()
