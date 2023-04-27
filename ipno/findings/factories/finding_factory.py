import factory
from factory.django import DjangoModelFactory
from faker import Faker

from findings.models import Finding

fake = Faker()


class FindingFactory(DjangoModelFactory):
    class Meta:
        model = Finding

    title = factory.LazyFunction(lambda: fake.word())
    description = factory.LazyFunction(lambda: fake.sentence())
    card_title = factory.LazyFunction(lambda: fake.word())
    card_author = factory.LazyFunction(lambda: fake.word())
    card_department = factory.LazyFunction(lambda: fake.word())
