from google.oauth2 import service_account

from .base import *  # NOQA
from .base import shared_processors

DEBUG = True

TEST = True

CORS_ORIGIN_WHITELIST = [
    "http://localhost:9090",
]

ELASTICSEARCH_DSL = {
    "default": {
        "hosts": env.str("ELASTICSEARCH_HOST", "elasticsearch-itest:9200"),
    },
}

DATABASES = {
    "default": {
        "ENGINE": "django_db_geventpool.backends.postgresql_psycopg2",
        "NAME": env.str("POSTGRES_DB", "ipno"),
        "USER": env.str("POSTGRES_USER", "ipno"),
        "PASSWORD": env.str("POSTGRES_PASSWORD", "ipno"),
        "HOST": env.str("POSTGRES_HOST_TEST", "localhost"),
        "PORT": 5432,
        "CONN_MAX_AGE": 0,
        "OPTIONS": {"MAX_CONNS": 20, "REUSE_CONNS": 10},
    }
}

INTERNAL_IPS = ["127.0.0.1"]

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=365),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=365 * 5),
}

GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    f"{BASE_DIR}/gcloud-credentials.json"  # NOQA
)

DOCUMENTS_BUCKET_NAME = "llead-documents-develop"
GC_PATH = f"https://storage.googleapis.com/{DOCUMENTS_BUCKET_NAME}/"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

HOST = os.getenv("HOST", "localhost:9090")
SERVER_URL = os.getenv("SERVER_URL", "web:9000")

FLUENT_PYTHON_LOG_FILE = "/var/log/python.log"

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
