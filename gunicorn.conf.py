import sys
from logging import Filter, getLogger
from gunicorn.glogging import Logger


bind = "0.0.0.0:8000"
loglevel = "info"
accesslog = '-'
errorlog = '-'

worker_class = 'gevent'
workers = 3


class HealthCheckFilter(Filter):
    def filter(self, record):
        return record.getMessage().find('/api/status/') == -1


class CustomGunicornLogger(Logger):
    def setup(self, cfg):
        super().setup(cfg)
        logger = getLogger("gunicorn.access")
        logger.addFilter(HealthCheckFilter())


logger_class = CustomGunicornLogger

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
