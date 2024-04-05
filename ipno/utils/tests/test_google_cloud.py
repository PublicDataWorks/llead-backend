from django.conf import settings
from django.test.testcases import TestCase

from mock import Mock, patch

from utils.google_cloud import GoogleCloudService


class GoogleCloudTestCase(TestCase):
    @patch("utils.google_cloud.Client")
    def test_upload_file_from_url(self, mock_client):
        mock_upload_from_string = Mock()
        mock_blob = Mock(return_value=Mock(upload_from_string=mock_upload_from_string))
        mock_bucket = Mock(return_value=Mock(blob=mock_blob))
        mock_storage_client = Mock(bucket=mock_bucket)
        mock_client.return_value = mock_storage_client

        google_cloud_service = GoogleCloudService(settings.DOCUMENTS_BUCKET_NAME)

        file_blob = "file_blob"
        destination_url = "destination_url"
        content_type = "application/pdf"
        google_cloud_service.upload_file_from_string(
            destination_url, file_blob, content_type
        )

        mock_client.assert_called()
        mock_bucket.assert_called_with(settings.DOCUMENTS_BUCKET_NAME)
        mock_blob.assert_called_with(destination_url)
        mock_upload_from_string.assert_called_with(file_blob, content_type=content_type)

    @patch("utils.google_cloud.Client")
    def test_delete_file_from_url(self, mock_client):
        mock_delete = Mock()
        mock_blob = Mock(return_value=Mock(delete=mock_delete))
        mock_bucket = Mock(return_value=Mock(blob=mock_blob))
        mock_storage_client = Mock(bucket=mock_bucket)
        mock_client.return_value = mock_storage_client

        google_cloud_service = GoogleCloudService(settings.DOCUMENTS_BUCKET_NAME)

        destination_url = "destination_url"
        google_cloud_service.delete_file_from_url(destination_url)

        mock_client.assert_called()
        mock_bucket.assert_called_with(settings.DOCUMENTS_BUCKET_NAME)
        mock_blob.assert_called_with(destination_url)
        mock_delete.assert_called()

    @patch("utils.google_cloud.Client")
    def test_is_object_exists(self, mock_client):
        mock_is_object_exists = Mock()
        mock_blob = Mock(return_value=Mock(exists=mock_is_object_exists))
        mock_bucket = Mock(return_value=Mock(blob=mock_blob))
        mock_storage_client = Mock(bucket=mock_bucket)
        mock_client.return_value = mock_storage_client

        google_cloud_service = GoogleCloudService(settings.DOCUMENTS_BUCKET_NAME)

        object_path = "object_path"
        google_cloud_service.is_object_exists(object_path)

        mock_client.assert_called()
        mock_bucket.assert_called_with(settings.DOCUMENTS_BUCKET_NAME)
        mock_blob.assert_called_with(object_path)
        mock_is_object_exists.assert_called()

    @patch("utils.google_cloud.Client")
    def test_move_blob_internally(self, mock_client):
        mock_blob_return = "mock_blob_return"
        mock_blob = Mock(return_value=mock_blob_return)
        mock_copy_blob = Mock()
        mock_delete_blob = Mock()

        mock_bucket_return = Mock(
            blob=mock_blob, copy_blob=mock_copy_blob, delete_blob=mock_delete_blob
        )
        mock_bucket = Mock(return_value=mock_bucket_return)
        mock_storage_client = Mock(bucket=mock_bucket)
        mock_client.return_value = mock_storage_client

        google_cloud_service = GoogleCloudService(settings.DOCUMENTS_BUCKET_NAME)

        source_blob_name = "source_blob_name"
        destination_blob_name = "destination_blob_name"
        google_cloud_service.move_blob_internally(
            source_blob_name, destination_blob_name
        )

        mock_client.assert_called()
        mock_bucket.assert_called_with(settings.DOCUMENTS_BUCKET_NAME)
        mock_blob.assert_called_with(source_blob_name)
        mock_copy_blob.assert_called_with(
            mock_blob_return, mock_bucket_return, destination_blob_name
        )
        mock_delete_blob.assert_called_with(source_blob_name)
