import factory
from faker import Faker

from news_articles.factories import NewsArticleFactory
from news_articles.models import MatchedSentence

fake = Faker()


class MatchedSentenceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MatchedSentence

    text = factory.LazyFunction(lambda: fake.sentence())
    article = factory.SubFactory(NewsArticleFactory)
