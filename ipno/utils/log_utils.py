from django.urls import reverse

from structlog import DropEvent


def drop_health_check_event(logger, method_name, event_dict):
    request = event_dict.get('request', '')
    if reverse('status') in request:
        raise DropEvent
    return event_dict
