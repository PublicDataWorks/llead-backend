from .base import *  # NOQA

CORS_ORIGIN_WHITELIST = [
    'http://localhost:9090',
]

TEST = True
WRGL_API_KEY = 'test-wrgl-api-key'
DROPBOX_APP_KEY = 'test-dropbox-app-key'
DROPBOX_APP_SECRET = 'test-dropbox-app-service'
DROPBOX_REFRESH_TOKEN = 'test-dropbox-refresh-token'

DOCUMENTS_BUCKET_NAME = 'llead-documents-test'
GC_PATH = f'https://storage.googleapis.com/{DOCUMENTS_BUCKET_NAME}/'

HOST = 'http://localhost:8080'
