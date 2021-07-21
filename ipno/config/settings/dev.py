from .base import *  # NOQA
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

GCLOUD_SUB_STORAGE = 'develop/'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
