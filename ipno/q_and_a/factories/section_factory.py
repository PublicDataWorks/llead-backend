import factory
from faker import Faker
from factory.django import DjangoModelFactory

from q_and_a.models import Section

fake = Faker()


class SectionFactory(DjangoModelFactory):
    class Meta:
        model = Section

    order = factory.LazyFunction(fake.pyint)
    name = factory.LazyFunction(fake.word)
