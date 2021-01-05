from .base import *  # NOQA

CORS_ORIGIN_WHITELIST = [
    'http://localhost:8080',
]

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'elasticsearch:9200'
    },
}
