import factory
from faker import Faker
from factory.django import DjangoModelFactory

from app_config.models import AppConfig, AppTextContent

fake = Faker()


class AppConfigFactory(DjangoModelFactory):
    class Meta:
        model = AppConfig

    name = factory.LazyFunction(fake.word)
    value = factory.LazyFunction(fake.word)


class AppTextContentFactory(DjangoModelFactory):
    class Meta:
        model = AppTextContent

    name = factory.LazyFunction(fake.word)
    value = factory.LazyFunction(fake.word)
