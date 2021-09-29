import factory
from faker import Faker

from news_articles.models import ExcludeOfficer

fake = Faker()


class ExcludeOfficerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExcludeOfficer
