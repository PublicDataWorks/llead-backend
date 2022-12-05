from gevent import monkey
from psycogreen.gevent import patch_psycopg

bind = "0.0.0.0:8000"
loglevel = "info"
accesslog = None
errorlog = '-'

worker_class = 'gevent'
workers = 3

monkey.patch_all()


def do_post_fork(server, worker):
    patch_psycopg()

    worker.log.info("Made Psycopg2 Green")


post_fork = do_post_fork

logconfig_dict = {
    'version': 1,
    'disable_existing_loggers': False,
    "handlers": {
        "console": {
            "class": "google.cloud.logging.handlers.StructuredLogHandler",
        },
    },
    "loggers": {
        "gunicorn.error": {
            "handlers": ["console"],
            "level": "INFO",
        },
    }
}
