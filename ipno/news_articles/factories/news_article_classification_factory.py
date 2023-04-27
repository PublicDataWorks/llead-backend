import factory
from faker import Faker

from news_articles.models import NewsArticleClassification

fake = Faker()


class NewsArticleClassificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NewsArticleClassification

    text = factory.LazyFunction(lambda: fake.sentence())
