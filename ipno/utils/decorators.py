from functools import wraps

from django.conf import settings
from django.http import Http404


def test_util_api(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    def raise404(*args, **kwargs):
        raise Http404

    if not settings.TEST:
        return raise404
    return wrapper
