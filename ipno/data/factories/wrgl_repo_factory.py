import factory
from faker import Faker

from data.models import WrglRepo

fake = Faker()


class WrglRepoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WrglRepo

    data_model = factory.LazyFunction(lambda: fake.word())
    repo_name = factory.LazyFunction(lambda: fake.word())
