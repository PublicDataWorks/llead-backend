import factory
from faker import Faker

from news_articles.factories.news_article_source_factory import NewsArticleSourceFactory
from news_articles.models import CrawledPost

fake = Faker()


class CrawledPostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CrawledPost

    source = factory.SubFactory(NewsArticleSourceFactory)
    post_guid = factory.LazyFunction(lambda: fake.uuid4())
