import factory
import pytz
from faker import Faker
from factory.django import DjangoModelFactory

from historical_data.models import AnonymousItem

fake = Faker()


class AnonymousItemFactory(DjangoModelFactory):
    class Meta:
        model = AnonymousItem

    item_id = factory.LazyFunction(fake.word)
    item_type = factory.LazyFunction(fake.word)
    last_visited = factory.LazyFunction(lambda: fake.date_time(tzinfo=pytz.utc))
