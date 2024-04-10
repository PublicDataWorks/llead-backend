import os
from shutil import rmtree

from django.conf import settings

import structlog
from google.cloud.storage import Client, transfer_manager

from ipno.data.constants import (
    AGENCY_MODEL_NAME,
    APPEAL_MODEL_NAME,
    BRADY_MODEL_NAME,
    CITIZEN_MODEL_NAME,
    COMPLAINT_MODEL_NAME,
    DOCUMENT_MODEL_NAME,
    EVENT_MODEL_NAME,
    NEWS_ARTICLE_CLASSIFICATION_MODEL_NAME,
    OFFICER_MODEL_NAME,
    PERSON_MODEL_NAME,
    POST_OFFICE_HISTORY_MODEL_NAME,
    USE_OF_FORCE_MODEL_NAME,
)

csv_file_name_mapping = {
    AGENCY_MODEL_NAME: "data_agency.csv",
    OFFICER_MODEL_NAME: "data_personnel.csv",
    NEWS_ARTICLE_CLASSIFICATION_MODEL_NAME: "data_news_article_classification.csv",
    COMPLAINT_MODEL_NAME: "data_allegation.csv",
    BRADY_MODEL_NAME: "data_brady.csv",
    USE_OF_FORCE_MODEL_NAME: "data_use-of-force.csv",
    CITIZEN_MODEL_NAME: "data_citizens.csv",
    APPEAL_MODEL_NAME: "data_appeal-hearing.csv",
    EVENT_MODEL_NAME: "data_event.csv",
    DOCUMENT_MODEL_NAME: "data_documents.csv",
    POST_OFFICE_HISTORY_MODEL_NAME: "data_post-officer-history.csv",
    PERSON_MODEL_NAME: "data_person.csv",
}

logger = structlog.get_logger("IPNO")


class GoogleCloudService:
    def __init__(self, bucket_name):
        storage_client = Client()
        self.bucket = storage_client.bucket(bucket_name)

    def upload_file_from_string(self, destination_location, file_blob, content_type):
        blob = self.bucket.blob(destination_location)
        blob.upload_from_string(file_blob, content_type=content_type)

    def delete_file_from_url(self, file_url):
        blob = self.bucket.blob(file_url)
        blob.delete()

    def is_object_exists(self, object_path):
        blob = self.bucket.blob(object_path)
        return blob.exists()

    def move_blob_internally(self, source_blob_name, destination_blob_name):
        """Moves a blob inside a bucket with a new name."""
        source_blob = self.bucket.blob(source_blob_name)

        self.bucket.copy_blob(source_blob, self.bucket, destination_blob_name)
        self.bucket.delete_blob(source_blob_name)

    def download_csv_data_sequentially(self, folder_name):
        blob_names = [
            f"{folder_name}/{csv_file_name_mapping[model]}"
            for model in csv_file_name_mapping
        ]

        if not os.path.exists(f"{settings.CSV_DATA_PATH}/{folder_name}"):
            os.makedirs(f"{settings.CSV_DATA_PATH}/{folder_name}")

        try:
            for name in blob_names:
                blob = self.bucket.blob(name)
                blob.download_to_filename(f"{settings.CSV_DATA_PATH}/{name}")
                logger.info("Successfully downloaded {}".format(name))
        except Exception as e:
            logger.error(
                "Failed to download raw data due to exception: {}".format(str(e))
            )
            rmtree(f"{settings.CSV_DATA_PATH}/{folder_name}")
            raise Exception(
                "Failed to download data from Google Cloud Storage, file name {}"
                .format(name)
            )

        downloaded_data = {
            model_name: f"{settings.CSV_DATA_PATH}/{folder_name}/{csv_file_name_mapping[model_name]}"
            for model_name in csv_file_name_mapping
        }

        return downloaded_data

    def download_csv_data(self, folder_name):
        blob_names = [
            f"{folder_name}/{csv_file_name_mapping[model]}"
            for model in csv_file_name_mapping
        ]

        results = transfer_manager.download_many_to_path(
            self.bucket, blob_names, destination_directory=settings.CSV_DATA_PATH
        )

        for name, result in zip(blob_names, results):
            if isinstance(result, Exception):
                logger.error(
                    "Failed to download {} due to exception: {}".format(name, result)
                )
                rmtree(f"{settings.CSV_DATA_PATH}/{folder_name}")
                raise Exception(
                    "Failed to download data from Google Cloud Storage, file name {}"
                    .format(name)
                )
            else:
                logger.info("Successfully downloaded {}".format(name))

        downloaded_data = {
            model_name: f"{settings.CSV_DATA_PATH}/{folder_name}/{csv_file_name_mapping[model_name]}"
            for model_name in csv_file_name_mapping
        }

        return downloaded_data
