from django.test.testcases import TestCase

from officers.factories import EventFactory


class EventTestCase(TestCase):
    def test_str(self):
        event = EventFactory()
        assert str(event) == f"{event.kind} - {event.id} - {event.event_uid[:5]}"

    def test_str_if_no_kind(self):
        event = EventFactory(kind=None)
        assert str(event) == f" - {event.id} - {event.event_uid[:5]}"
