import factory
from faker import Faker

from news_articles.models import NewsArticleSource

fake = Faker()


class NewsArticleSourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NewsArticleSource

    source_name = factory.LazyFunction(lambda: fake.word())
    source_display_name = factory.LazyFunction(lambda: fake.word())
