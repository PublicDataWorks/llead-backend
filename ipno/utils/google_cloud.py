from django.conf import settings

from google.cloud.storage import Client


class GoogleCloudService:
    def __init__(self):
        storage_client = Client()
        bucket = storage_client.bucket(settings.DOCUMENTS_BUCKET_NAME)
        self.bucket = bucket

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
