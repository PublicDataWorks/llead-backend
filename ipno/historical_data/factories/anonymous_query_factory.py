import factory
import pytz
from factory.django import DjangoModelFactory
from faker import Faker

from historical_data.models import AnonymousQuery

fake = Faker()


class AnonymousQueryFactory(DjangoModelFactory):
    class Meta:
        model = AnonymousQuery

    query = factory.LazyFunction(fake.word)
    last_visited = factory.LazyFunction(lambda: fake.date_time(tzinfo=pytz.utc))
