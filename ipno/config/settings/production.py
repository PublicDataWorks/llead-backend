import os

from google.oauth2 import service_account

from .base import *  # NOQA

DEBUG = False

CORS_ORIGIN_WHITELIST = [
    "https://llead.co",
]

GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    f"{BASE_DIR}/gcloud-credentials.json"  # NOQA
)

DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
GS_BUCKET_NAME = "llead-static"
DOCUMENTS_BUCKET_NAME = "llead-documents"
RAW_DATA_BUCKET_NAME = "llead-raw-data"
GC_DOCUMENT_BUCKET_PATH = f"https://storage.googleapis.com/{DOCUMENTS_BUCKET_NAME}/"
GC_RAW_DATA_BUCKET_PATH = f"https://storage.googleapis.com/{RAW_DATA_BUCKET_NAME}/"

HOST = os.getenv("HOST", "https://llead.co")
SERVER_URL = os.getenv("SERVER_URL", "https://api.llead.co")

EMAIL_BACKEND = "anymail.backends.sendinblue.EmailBackend"

ANYMAIL = {
    "SENDINBLUE_API_KEY": os.getenv("SENDINBLUE_API_KEY", ""),
}
