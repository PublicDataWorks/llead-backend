from django.conf import settings

from pytest import raises
from django.test.testcases import TestCase, override_settings
from mock import Mock, MagicMock, patch

from utils.dropbox_utils import DropboxService


class DropboxServiceTestCase(TestCase):
    @override_settings(DROPBOX_REFRESH_TOKEN='dropbox-refresh-token')
    @patch('builtins.input')
    @patch('utils.dropbox_utils.DropboxOAuth2FlowNoRedirect')
    def test_generate_new_dropbox_token_success(self, MockDropboxOAuth2FlowNoRedirect, MockInput):
        mock_auth_flow_start = MagicMock()
        mock_auth_flow_finish = MagicMock()
        mock_auth_flow_finish.return_value = Mock(refresh_token='dropbox_refresh_token')

        mock_auth_flow = MagicMock()
        mock_auth_flow.start = mock_auth_flow_start
        mock_auth_flow.finish = mock_auth_flow_finish
        MockDropboxOAuth2FlowNoRedirect.return_value = mock_auth_flow

        MockInput.return_value = 'authorization_code'

        DropboxService.generate_dropbox_token()

        assert MockDropboxOAuth2FlowNoRedirect.call_args[0] == (
            settings.DROPBOX_APP_KEY,
            settings.DROPBOX_APP_SECRET,
        )

        assert MockDropboxOAuth2FlowNoRedirect.call_args[1] == {
            'token_access_type': 'offline'
        }

    @override_settings(DROPBOX_REFRESH_TOKEN='dropbox-refresh-token')
    @patch('utils.dropbox_utils.Dropbox')
    def test_init_dropbox_service_success(self, MockDropBox):
        mock_dropbox_client = MagicMock()

        MockDropBox.return_value = mock_dropbox_client

        dropbox_service = DropboxService()

        MockDropBox.assert_called_with(
            oauth2_refresh_token='dropbox-refresh-token',
            app_key=settings.DROPBOX_APP_KEY,
            app_secret=settings.DROPBOX_APP_SECRET,
        )

        assert dropbox_service.dropbox_client == mock_dropbox_client

    @override_settings(DROPBOX_REFRESH_TOKEN=None)
    def test_get_temporary_link_fail_due_to_missing_refresh_token(self):
        with raises(ValueError, match='No dropbox refresh token found, please init it first'):
            DropboxService()

    @override_settings(DROPBOX_REFRESH_TOKEN='dropbox-refresh-token')
    @patch('utils.dropbox_utils.Dropbox')
    def test_get_temporary_link_from_path_success(self, MockDropBox):
        mock_check_and_refresh_access_token = MagicMock()

        mock_files_get_temporary_link = MagicMock()
        mock_files_get_temporary_link.return_value = Mock(link='temporary_link')

        mock_dropbox_client = MagicMock()
        mock_dropbox_client.check_and_refresh_access_token = mock_check_and_refresh_access_token
        mock_dropbox_client.files_get_temporary_link = mock_files_get_temporary_link

        MockDropBox.return_value = mock_dropbox_client

        dropbox_service = DropboxService()

        path = 'any-url-path'

        download_link = dropbox_service.get_temporary_link_from_path(path)

        assert download_link == 'temporary_link'

        MockDropBox.assert_called_with(
            oauth2_refresh_token='dropbox-refresh-token',
            app_key=settings.DROPBOX_APP_KEY,
            app_secret=settings.DROPBOX_APP_SECRET,
        )
