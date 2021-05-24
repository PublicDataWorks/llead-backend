import json
from io import StringIO, BytesIO
from csv import DictWriter

from django.test.testcases import TestCase, override_settings

from mock import patch

from data.services import BaseImporter
from data.models import ImportLog
from data.constants import (
    IMPORT_LOG_STATUS_NO_NEW_COMMIT,
    IMPORT_LOG_STATUS_FINISHED,
    IMPORT_LOG_STATUS_ERROR
)
from data.factories import WrglRepoFactory


TEST_MODEL_NAME = 'TestModelName'


class TestImporter(BaseImporter):
    data_model = TEST_MODEL_NAME


class BaseImporterTestCase(TestCase):
    def setUp(self):
        csv_content = StringIO()
        writer = DictWriter(
            csv_content,
            fieldnames=['id', 'name']
        )
        writer.writeheader()
        writer.writerows([
            {
                'id': '1',
                'name': 'name 1',
            },
            {
                'id': '2',
                'name': 'name 2',
            },
            {
                'id': '3',
                'name': 'name 3',
            },
        ])
        self.csv_stream = BytesIO(csv_content.getvalue().encode('utf-8'))

    def test_process_wrgl_repo_not_found(self):
        TestImporter().process()

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == TEST_MODEL_NAME
        assert import_log.status == IMPORT_LOG_STATUS_ERROR
        assert import_log.error_message == 'Cannot find Wrgl Repo!'
        assert import_log.finished_at

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    @patch('urllib.request.urlopen')
    def test_process_invalid_wrgl_repo_name(self, urlopen_mock):
        WrglRepoFactory(
            data_model=TEST_MODEL_NAME,
            repo_name='test_repo_name'
        )

        repo_details_stream = BytesIO(json.dumps({}).encode('utf-8'))
        urlopen_mock.return_value = repo_details_stream

        TestImporter().process()

        repo_details_request = urlopen_mock.call_args[0][0]
        assert repo_details_request._full_url == 'https://www.wrgl.co/api/v1/users/wrgl_user/repos/test_repo_name'
        assert repo_details_request.headers == {
            'Authorization': 'APIKEY wrgl-api-key'
        }

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == TEST_MODEL_NAME
        assert import_log.status == IMPORT_LOG_STATUS_ERROR
        assert import_log.error_message == 'Cannot get latest commit hash from Wrgl for repo test_repo_name!'
        assert import_log.finished_at

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    @patch('urllib.request.urlopen')
    def test_process_no_new_commit(self, urlopen_mock):
        WrglRepoFactory(
            data_model=TEST_MODEL_NAME,
            repo_name='test_repo_name',
            commit_hash='3950bd17edfd805972781ef9fe2c6449'
        )

        data = {
            'hash': '3950bd17edfd805972781ef9fe2c6449'
        }
        repo_details_stream = BytesIO(json.dumps(data).encode('utf-8'))
        urlopen_mock.return_value = repo_details_stream

        TestImporter().process()

        repo_details_request = urlopen_mock.call_args[0][0]
        assert repo_details_request._full_url == 'https://www.wrgl.co/api/v1/users/wrgl_user/repos/test_repo_name'
        assert repo_details_request.headers == {
            'Authorization': 'APIKEY wrgl-api-key'
        }

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == TEST_MODEL_NAME
        assert import_log.status == IMPORT_LOG_STATUS_NO_NEW_COMMIT
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert not import_log.error_message
        assert import_log.finished_at

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    @patch('data.services.base_importer.BaseImporter.import_data')
    @patch('urllib.request.urlopen')
    def test_process_error_while_processing_data(self, urlopen_mock, import_data_mock):
        WrglRepoFactory(
            data_model=TEST_MODEL_NAME,
            repo_name='test_repo_name',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        data = {
            'hash': '3950bd17edfd805972781ef9fe2c6449'
        }
        repo_details_stream = BytesIO(json.dumps(data).encode('utf-8'))
        urlopen_mock.side_effect = [repo_details_stream, self.csv_stream]
        import_data_mock.side_effect = Exception()

        TestImporter().process()

        repo_details_request = urlopen_mock.call_args_list[0][0][0]
        assert repo_details_request._full_url == 'https://www.wrgl.co/api/v1/users/wrgl_user/repos/test_repo_name'
        assert repo_details_request.headers == {
            'Authorization': 'APIKEY wrgl-api-key'
        }

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == TEST_MODEL_NAME
        assert import_log.status == IMPORT_LOG_STATUS_ERROR
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert 'Error occurs while importing data!' in import_log.error_message
        assert import_log.finished_at

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    @patch('data.services.base_importer.BaseImporter.import_data')
    @patch('urllib.request.urlopen')
    def test_process_successfully(self, urlopen_mock, import_data_mock):
        WrglRepoFactory(
            data_model=TEST_MODEL_NAME,
            repo_name='test_repo_name',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        data = {
            'hash': '3950bd17edfd805972781ef9fe2c6449'
        }
        repo_details_stream = BytesIO(json.dumps(data).encode('utf-8'))
        urlopen_mock.side_effect = [repo_details_stream, self.csv_stream]
        import_data_mock.return_value = {
            'created_rows': 3,
            'updated_rows': 5,
            'deleted_rows': 1,
        }

        TestImporter().process()

        repo_details_request = urlopen_mock.call_args_list[0][0][0]
        assert repo_details_request._full_url == 'https://www.wrgl.co/api/v1/users/wrgl_user/repos/test_repo_name'
        assert repo_details_request.headers == {
            'Authorization': 'APIKEY wrgl-api-key'
        }

        import_data_mock.assert_called_with(
            [
                {'id': '1', 'name': 'name 1'},
                {'id': '2', 'name': 'name 2'},
                {'id': '3', 'name': 'name 3'}
            ]
        )

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == TEST_MODEL_NAME
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 3
        assert import_log.updated_rows == 5
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at
