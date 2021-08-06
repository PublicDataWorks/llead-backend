import os

from .base import *  # NOQA
from google.oauth2 import service_account
from datetime import timedelta

INSTALLED_APPS += (  # NOQA
    'debug_toolbar',
    'django_extensions',
)

CORS_ORIGIN_WHITELIST = [
    'http://localhost:8080',
]

INTERNAL_IPS = ['127.0.0.1']

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']  # NOQA
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] += ('rest_framework.renderers.BrowsableAPIRenderer',)  # NOQA

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=365),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=365 * 5),
}


def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
}

DEBUG = True

GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    f'{BASE_DIR}/gcloud-credentials.json'  # NOQA
)

DOCUMENTS_BUCKET_NAME = 'llead-documents-develop'
GC_PATH = f'https://storage.googleapis.com/{DOCUMENTS_BUCKET_NAME}/'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

HOST = os.getenv('HOST', 'localhost:8080')
