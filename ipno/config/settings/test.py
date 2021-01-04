from .base import *

CORS_ORIGIN_WHITELIST = [
    'http://localhost:9090',
]

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'elasticsearch:9200'
    },
}
