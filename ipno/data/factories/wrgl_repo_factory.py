import factory
from faker import Faker

from data.models import WrglRepo

fake = Faker()


class WrglRepoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WrglRepo
