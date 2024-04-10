from django.conf import settings
from django.test.testcases import TestCase

from mock import Mock, call, patch

from utils.google_cloud import GoogleCloudService, csv_file_name_mapping


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

    @patch("utils.google_cloud.transfer_manager")
    @patch("utils.google_cloud.Client")
    def test_download_csv_data(self, mock_client, mock_transfer_manager):
        mock_transfer_manager.download_many_to_path = Mock(
            return_value=[None] * len(csv_file_name_mapping)
        )

        mock_bucket = Mock(return_value="mock_bucket")
        mock_storage_client = Mock(bucket=mock_bucket)
        mock_client.return_value = mock_storage_client

        google_cloud_service = GoogleCloudService("bucket_name")

        folder_name = "folder_name"

        result = google_cloud_service.download_csv_data(folder_name)

        mock_client.assert_called()
        mock_bucket.assert_called_with("bucket_name")
        mock_transfer_manager.download_many_to_path.assert_called_with(
            "mock_bucket",
            [
                f"{folder_name}/{csv_file_name_mapping[model]}"
                for model in csv_file_name_mapping
            ],
            destination_directory=settings.CSV_DATA_PATH,
        )

        assert result == {
            model_name: f"{settings.CSV_DATA_PATH}/{folder_name}/{csv_file_name_mapping[model_name]}"
            for model_name in csv_file_name_mapping
        }

    @patch("utils.google_cloud.rmtree")
    @patch("utils.google_cloud.transfer_manager")
    @patch("utils.google_cloud.Client")
    def test_download_csv_data_raise_error_and_delete_files(
        self, mock_client, mock_transfer_manager, mock_rmtree
    ):
        mock_transfer_manager.download_many_to_path = Mock(
            return_value=[None] * (len(csv_file_name_mapping) - 1)
            + [Exception("Failed to download")]
        )

        mock_bucket = Mock(return_value="mock_bucket")
        mock_storage_client = Mock(bucket=mock_bucket)
        mock_client.return_value = mock_storage_client

        google_cloud_service = GoogleCloudService("bucket_name")

        folder_name = "folder_name"

        with self.assertRaises(Exception) as e:
            google_cloud_service.download_csv_data(folder_name)

        assert str(
            e.exception
        ) == "Failed to download data from Google Cloud Storage, file name {}".format(
            "folder_name/data_person.csv"
        )

        mock_client.assert_called()
        mock_bucket.assert_called_with("bucket_name")
        mock_transfer_manager.download_many_to_path.assert_called_with(
            "mock_bucket",
            [
                f"{folder_name}/{csv_file_name_mapping[model]}"
                for model in csv_file_name_mapping
            ],
            destination_directory=settings.CSV_DATA_PATH,
        )

        mock_rmtree.assert_called_with(f"{settings.CSV_DATA_PATH}/{folder_name}")

    @patch("utils.google_cloud.os")
    @patch("utils.google_cloud.rmtree")
    @patch("utils.google_cloud.Client")
    def test_download_csv_data_sequentially(self, mock_client, mock_rmtree, mock_os):
        mock_os.path.exists.return_value = False

        mock_download_to_filename = Mock()
        mock_blob = Mock(
            return_value=Mock(download_to_filename=mock_download_to_filename)
        )
        mock_bucket = Mock(return_value=Mock(blob=mock_blob))
        mock_storage_client = Mock(bucket=mock_bucket)
        mock_client.return_value = mock_storage_client

        google_cloud_service = GoogleCloudService("bucket_name")
        google_cloud_service.download_csv_data_sequentially("test_folder")

        mock_os.makedirs.assert_called_with(f"{settings.CSV_DATA_PATH}/test_folder")
        mock_blob.assert_has_calls(
            [
                call("test_folder/data_agency.csv"),
                call("test_folder/data_personnel.csv"),
                call("test_folder/data_news_article_classification.csv"),
                call("test_folder/data_allegation.csv"),
                call("test_folder/data_brady.csv"),
                call("test_folder/data_use-of-force.csv"),
                call("test_folder/data_citizens.csv"),
                call("test_folder/data_appeal-hearing.csv"),
                call("test_folder/data_event.csv"),
                call("test_folder/data_documents.csv"),
                call("test_folder/data_post-officer-history.csv"),
                call("test_folder/data_person.csv"),
            ]
        )
        mock_download_to_filename.assert_has_calls(
            [
                call(f"{settings.CSV_DATA_PATH}/test_folder/data_agency.csv"),
                call(f"{settings.CSV_DATA_PATH}/test_folder/data_personnel.csv"),
                call(
                    f"{settings.CSV_DATA_PATH}/test_folder/data_news_article_classification.csv"
                ),
                call(f"{settings.CSV_DATA_PATH}/test_folder/data_allegation.csv"),
                call(f"{settings.CSV_DATA_PATH}/test_folder/data_brady.csv"),
                call(f"{settings.CSV_DATA_PATH}/test_folder/data_use-of-force.csv"),
                call(f"{settings.CSV_DATA_PATH}/test_folder/data_citizens.csv"),
                call(f"{settings.CSV_DATA_PATH}/test_folder/data_appeal-hearing.csv"),
                call(f"{settings.CSV_DATA_PATH}/test_folder/data_event.csv"),
                call(f"{settings.CSV_DATA_PATH}/test_folder/data_documents.csv"),
                call(
                    f"{settings.CSV_DATA_PATH}/test_folder/data_post-officer-history.csv"
                ),
                call(f"{settings.CSV_DATA_PATH}/test_folder/data_person.csv"),
            ]
        )
        mock_rmtree.assert_not_called()

    @patch("utils.google_cloud.os")
    @patch("utils.google_cloud.rmtree")
    @patch("utils.google_cloud.Client")
    def test_download_csv_data_sequentially_fail(
        self, mock_client, mock_rmtree, mock_os
    ):
        mock_os.path.exists.return_value = False

        mock_download_to_filename = Mock()
        mock_download_to_filename.side_effect = Exception()
        mock_blob = Mock(
            return_value=Mock(download_to_filename=mock_download_to_filename)
        )
        mock_bucket = Mock(return_value=Mock(blob=mock_blob))
        mock_storage_client = Mock(bucket=mock_bucket)
        mock_client.return_value = mock_storage_client

        google_cloud_service = GoogleCloudService("bucket_name")

        with self.assertRaises(Exception):
            google_cloud_service.download_csv_data_sequentially("test_folder")

        mock_os.makedirs.assert_called_with(f"{settings.CSV_DATA_PATH}/test_folder")
        mock_blob.assert_called_once()
        mock_rmtree.assert_called_with(f"{settings.CSV_DATA_PATH}/test_folder")
