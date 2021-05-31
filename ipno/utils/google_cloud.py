from google.cloud.storage import Client

from utils.constants import BUCKET_NAME


class GoogleCloudService:
    def __init__(self):
        storage_client = Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        self.bucket = bucket

    def upload_file_from_string(self, destination_location, file_blob, content_type):
        blob = self.bucket.blob(destination_location)
        blob.upload_from_string(file_blob, content_type=content_type)

    def delete_file_from_url(self, file_url):
        blob = self.bucket.blob(file_url)
        blob.delete()
