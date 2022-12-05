import structlog

from .base import *  # NOQA
from .base import shared_processors

CORS_ORIGIN_WHITELIST = [
    "http://localhost:9090",
]

TEST = True
WRGL_API_KEY = "test-wrgl-api-key"
DROPBOX_APP_KEY = "test-dropbox-app-key"
DROPBOX_APP_SECRET = "test-dropbox-app-service"
DROPBOX_REFRESH_TOKEN = "test-dropbox-refresh-token"

DOCUMENTS_BUCKET_NAME = "llead-documents-test"
GC_PATH = f"https://storage.googleapis.com/{DOCUMENTS_BUCKET_NAME}/"

HOST = "http://localhost:8080"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "plain_console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "foreign_pre_chain": shared_processors,
            "processors": [
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.dev.ConsoleRenderer(),
            ],
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "plain_console",
        },
    },
    "loggers": {
        "django_structlog": {
            "handlers": ["console"],
            "level": "INFO",
        },
        # Make sure to replace the following logger's name for yours
        "django_structlog_ipno": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}
