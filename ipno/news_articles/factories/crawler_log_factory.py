import factory
from faker import Faker

from news_articles.models import CrawlerLog

fake = Faker()


class CrawlerLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CrawlerLog

    source_name = factory.LazyFunction(lambda: fake.word())
    created_rows = factory.LazyFunction(lambda: fake.pyint())
    error_rows = factory.LazyFunction(lambda: fake.pyint())
