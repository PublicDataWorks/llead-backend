from functools import lru_cache

import structlog

from config.celery import app

logger = structlog.get_logger("IPNO")


@lru_cache
def check_app_ping():
    app_ping = bool(app.control.ping())

    if not app_ping:
        logger.error("Celery app is not healthy, please check.")
        return False

    return True


def run_task(func):
    def wrapper(*args, **kwargs):
        if check_app_ping():
            func.delay(*args, **kwargs)
        else:
            func(*args, **kwargs)

    return wrapper
