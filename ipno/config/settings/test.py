from .base import *  # NOQA

CORS_ORIGIN_WHITELIST = [
    'http://localhost:9090',
]

TEST = True

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'elasticsearch:9200'
    },
}
