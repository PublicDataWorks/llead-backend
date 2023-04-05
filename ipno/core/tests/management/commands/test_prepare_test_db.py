from django.core.management import call_command
from django.test import TestCase

from authentication.factories import User
from historical_data.factories import AnonymousItemFactory, AnonymousQueryFactory
from historical_data.models import AnonymousItem, AnonymousQuery


class PrepareTestDBCommandTestCase(TestCase):
    def test_handle(self):
        AnonymousItemFactory()
        AnonymousQueryFactory()

        call_command("prepare_test_db")

        assert len(User.objects.all()) == 2
        assert User.objects.filter(email="admin@gmail.com").first().is_admin
        assert not User.objects.filter(email="test@gmail.com").first().is_admin
        assert len(AnonymousItem.objects.all()) == 0
        assert len(AnonymousQuery.objects.all()) == 0
