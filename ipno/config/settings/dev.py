from .base import *  # NOQA
from datetime import timedelta

CORS_ORIGIN_WHITELIST = [
    'http://localhost:8080',
]

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'elasticsearch:9200'
    },
}

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] += ('rest_framework.renderers.BrowsableAPIRenderer',)  # NOQA

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=365),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=365 * 5),
}
