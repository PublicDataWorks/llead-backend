from django.core.management import call_command
from django.test import TestCase

from mock import patch


class UpdateFieldCommandTestCase(TestCase):
    @patch('data.services.DataTroubleshooting')
    def test_call_command(self, data_troubleshooting_mock):
        data_troubleshooting_mock.return_value.process.return_value = True

        call_command('update_field')

        data_troubleshooting_mock.assert_called()
