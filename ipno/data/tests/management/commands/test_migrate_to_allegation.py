from django.core.management import call_command
from django.test import TestCase

from mock import patch

from data.factories import WrglRepoFactory
from data.models import WrglRepo


class MigrateToAllegationCommandTestCase(TestCase):
    @patch('utils.count_complaints.count_complaints')
    @patch('data.services.new_complaint_importer.NewComplaintImporter.process')
    def test_call_command(
            self,
            new_complaint_process_mock,
            count_complaints_mock,
    ):
        WrglRepoFactory(repo_name='complaint')
        new_complaint_process_mock.return_value = True
        call_command('migrate_to_allegation')

        new_complaint_process_mock.assert_called()
        count_complaints_mock.assert_called()

        wrgl_repo = WrglRepo.objects.first()
        assert wrgl_repo
        assert wrgl_repo.repo_name == 'allegation'
        assert not wrgl_repo.commit_hash

    @patch('utils.count_complaints.count_complaints')
    @patch('data.services.new_complaint_importer.NewComplaintImporter.process')
    def test_call_command_with_no_new_data(
            self,
            new_complaint_process_mock,
            count_complaints_mock,
    ):
        new_complaint_process_mock.return_value = False
        call_command('migrate_to_allegation')

        new_complaint_process_mock.assert_called()
        count_complaints_mock.assert_not_called()
