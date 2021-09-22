import sys

bind = "0.0.0.0:8000"
loglevel = "info"
accesslog = '/var/log/access.log'
errorlog = '/var/log/error.log'

logconfig_dict = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'stream': sys.stdout
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
