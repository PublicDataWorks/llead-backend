import factory
from factory.django import DjangoModelFactory
from faker import Faker

from app_config.models import (
    AppTextContent,
    AppValueConfig,
    FrontPageCard,
    FrontPageOrder,
)

fake = Faker()


class AppValueConfigFactory(DjangoModelFactory):
    class Meta:
        model = AppValueConfig

    name = factory.LazyFunction(fake.word)
    value = factory.LazyFunction(fake.word)


class AppTextContentFactory(DjangoModelFactory):
    class Meta:
        model = AppTextContent

    name = factory.LazyFunction(fake.word)
    value = factory.LazyFunction(fake.word)


class FrontPageOrderFactory(DjangoModelFactory):
    class Meta:
        model = FrontPageOrder

    section = factory.LazyFunction(fake.word)
    order = factory.LazyFunction(fake.pyint)


class FrontPageCardFactory(DjangoModelFactory):
    class Meta:
        model = FrontPageCard

    order = factory.LazyFunction(fake.pyint)
    content = factory.LazyFunction(fake.word)
