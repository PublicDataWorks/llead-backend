import factory
from faker import Faker

from news_articles.models import NewsArticleSource

fake = Faker()


class NewsArticleSourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NewsArticleSource

    source_name = factory.LazyFunction(lambda: fake.word())
    custom_matching_name = factory.LazyFunction(lambda: fake.word())
