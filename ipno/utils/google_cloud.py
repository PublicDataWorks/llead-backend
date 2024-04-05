from datetime import datetime

from google.cloud.storage import Client, transfer_manager


class GoogleCloudService:
    def __init__(self, bucket_name, **kwargs):
        storage_client = Client()
        self.bucket = storage_client.bucket(bucket_name)
        self.data_mapping = kwargs.get("data_mapping", {})
        self.csv_file_name_mapping = kwargs.get("csv_file_name_mapping", {})
        self.csv_data_path = kwargs.get("csv_data_path", "")

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

    def download_csv_data(self):
        folder_name = datetime.now().strftime("%Y%m%d")
        blob_names = [
            f"{folder_name}/{self.csv_file_name_mapping[model]}"
            for model in self.data_mapping
        ]

        results = transfer_manager.download_many_to_path(
            self.bucket, blob_names, destination_directory=self.csv_data_path
        )

        for name, result in zip(blob_names, results):
            if isinstance(result, Exception):
                print("Failed to download {} due to exception: {}".format(name, result))
            else:
                print("Successfully downloaded {}".format(name))
