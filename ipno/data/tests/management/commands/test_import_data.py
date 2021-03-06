from django.core.management import call_command
from django.test import TestCase

from mock import patch


class CreateInitialWRGLReposCommandTestCase(TestCase):
    def setUp(self):
        self.patcher = patch('data.services.document_importer.GoogleCloudService')
        self.patcher.start()

    @patch('django.core.cache.cache.clear')
    @patch('utils.count_complaints.count_complaints')
    @patch('utils.search_index.rebuild_search_index')
    @patch('utils.data_utils.compute_department_data_period')
    @patch('data.services.event_importer.EventImporter.process')
    @patch('data.services.complaint_importer.ComplaintImporter.process')
    @patch('data.services.uof_importer.UofImporter.process')
    @patch('data.services.uof_officer_importer.UofOfficerImporter.process')
    @patch('data.services.uof_citizen_importer.UofCitizenImporter.process')
    @patch('data.services.officer_importer.OfficerImporter.process')
    @patch('data.services.document_importer.DocumentImporter.process')
    @patch('data.services.person_importer.PersonImporter.process')
    @patch('data.services.appeal_importer.AppealImporter.process')
    def test_call_command(
            self,
            appeal_process_mock,
            person_process_mock,
            document_process_mock,
            officer_process_mock,
            uof_process_mock,
            uof_officer_process_mock,
            uof_citizen_process_mock,
            complaint_process_mock,
            event_process_mock,
            rebuild_search_index_mock,
            count_complaints_mock,
            compute_department_data_period_mock,
            cache_clear_mock,
    ):
        appeal_process_mock.return_value = True
        person_process_mock.return_value = True
        document_process_mock.return_value = True
        officer_process_mock.return_value = True
        uof_process_mock.return_value = False
        uof_officer_process_mock.return_value = True
        uof_citizen_process_mock.return_value = False
        complaint_process_mock.return_value = True
        event_process_mock.return_value = False
        call_command('import_data')

        appeal_process_mock.assert_called()
        person_process_mock.assert_called()
        document_process_mock.assert_called()
        officer_process_mock.assert_called()
        uof_process_mock.assert_called()
        uof_officer_process_mock.assert_called()
        uof_citizen_process_mock.assert_called()
        complaint_process_mock.assert_called()
        event_process_mock.assert_called()
        rebuild_search_index_mock.assert_called()
        count_complaints_mock.assert_called()
        compute_department_data_period_mock.assert_called()
        cache_clear_mock.assert_called()

    @patch('django.core.cache.cache.clear')
    @patch('utils.count_complaints.count_complaints')
    @patch('utils.search_index.rebuild_search_index')
    @patch('utils.data_utils.compute_department_data_period')
    @patch('data.services.event_importer.EventImporter.process')
    @patch('data.services.complaint_importer.ComplaintImporter.process')
    @patch('data.services.uof_importer.UofImporter.process')
    @patch('data.services.uof_officer_importer.UofOfficerImporter.process')
    @patch('data.services.uof_citizen_importer.UofCitizenImporter.process')
    @patch('data.services.officer_importer.OfficerImporter.process')
    @patch('data.services.document_importer.DocumentImporter.process')
    @patch('data.services.person_importer.PersonImporter.process')
    @patch('data.services.appeal_importer.AppealImporter.process')
    def test_call_command_with_no_new_data(
            self,
            appeal_process_mock,
            person_process_mock,
            document_process_mock,
            officer_process_mock,
            uof_process_mock,
            uof_officer_process_mock,
            uof_citizen_process_mock,
            complaint_process_mock,
            event_process_mock,
            rebuild_search_index_mock,
            count_complaints_mock,
            compute_department_data_period_mock,
            cache_clear_mock,
    ):
        appeal_process_mock.return_value = False
        person_process_mock.return_value = False
        document_process_mock.return_value = False
        officer_process_mock.return_value = False
        uof_process_mock.return_value = False
        uof_officer_process_mock.return_value = False
        uof_citizen_process_mock.return_value = False
        complaint_process_mock.return_value = False
        event_process_mock.return_value = False
        call_command('import_data')

        appeal_process_mock.assert_called()
        person_process_mock.assert_called()
        document_process_mock.assert_called()
        officer_process_mock.assert_called()
        uof_process_mock.assert_called()
        uof_officer_process_mock.assert_called()
        uof_citizen_process_mock.assert_called()
        complaint_process_mock.assert_called()
        event_process_mock.assert_called()
        rebuild_search_index_mock.assert_not_called()
        count_complaints_mock.assert_not_called()
        compute_department_data_period_mock.assert_not_called()
        cache_clear_mock.assert_not_called()
