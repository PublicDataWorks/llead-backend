from .base import *  # NOQA
from google.oauth2 import service_account

DEBUG = False

CORS_ORIGIN_WHITELIST = [
    'http://35.236.251.246',
]

GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    f'{BASE_DIR}/gcloud-credentials.json' # NOQA
)

DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = 'ipno-staging'

STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
