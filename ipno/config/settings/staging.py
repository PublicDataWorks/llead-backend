import os

from .base import *  # NOQA
from google.oauth2 import service_account

DEBUG = False

CORS_ORIGIN_WHITELIST = [
    'https://llead.co',
]

GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    f'{BASE_DIR}/gcloud-credentials.json'  # NOQA
)

DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = 'ipno-staging'

STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'

HOST = os.getenv('HOST', 'https://llead.co')

EMAIL_BACKEND = "anymail.backends.sendinblue.EmailBackend"

ANYMAIL = {
    "SENDINBLUE_API_KEY": os.getenv('SENDINBLUE_API_KEY', ''),
}

SENDINBLUE_API_URL = "https://api.sendinblue.com/v3/"
