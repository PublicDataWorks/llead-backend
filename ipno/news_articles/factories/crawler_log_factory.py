import factory
from faker import Faker

from news_articles.factories.news_article_source_factory import NewsArticleSourceFactory
from news_articles.models import CrawlerLog

fake = Faker()


class CrawlerLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CrawlerLog

    source = factory.SubFactory(NewsArticleSourceFactory)
    created_rows = factory.LazyFunction(lambda: fake.pyint())
    error_rows = factory.LazyFunction(lambda: fake.pyint())
