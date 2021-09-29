import factory
from faker import Faker

from news_articles.models import MatchingKeyword

fake = Faker()


class MatchingKeywordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MatchingKeyword
