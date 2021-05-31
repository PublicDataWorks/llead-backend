from django.test.testcases import TestCase
from mock import patch, Mock

from utils.google_cloud import GoogleCloudService


class GoogleCloudTestCase(TestCase):
    @patch('utils.google_cloud.Client')
    def test_upload_file_from_url(self, mock_client):
        mock_upload_from_string = Mock()
        mock_blob = Mock(return_value=Mock(upload_from_string=mock_upload_from_string))
        mock_bucket = Mock(return_value=Mock(blob=mock_blob))
        mock_storage_client = Mock(bucket=mock_bucket)
        mock_client.return_value = mock_storage_client

        google_cloud_service = GoogleCloudService()

        file_blob = 'file_blob'
        destination_url = 'destination_url'
        content_type = 'application/pdf'
        google_cloud_service.upload_file_from_string(destination_url, file_blob, content_type)

        mock_client.assert_called()
        mock_bucket.assert_called_with('llead-documents')
        mock_blob.assert_called_with(destination_url)
        mock_upload_from_string.assert_called_with(file_blob, content_type=content_type)

    @patch('utils.google_cloud.Client')
    def test_delete_file_from_url(self, mock_client):
        mock_delete = Mock()
        mock_blob = Mock(return_value=Mock(delete=mock_delete))
        mock_bucket = Mock(return_value=Mock(blob=mock_blob))
        mock_storage_client = Mock(bucket=mock_bucket)
        mock_client.return_value = mock_storage_client

        google_cloud_service = GoogleCloudService()

        destination_url = 'destination_url'
        google_cloud_service.delete_file_from_url(destination_url)

        mock_client.assert_called()
        mock_bucket.assert_called_with('llead-documents')
        mock_blob.assert_called_with(destination_url)
        mock_delete.assert_called()
