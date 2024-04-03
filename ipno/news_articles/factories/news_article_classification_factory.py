import factory
from faker import Faker

from news_articles.models import NewsArticleClassification

fake = Faker()


class NewsArticleClassificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NewsArticleClassification

    article_id = factory.LazyFunction(lambda: fake.pyint())
    text = factory.LazyFunction(lambda: fake.sentence())
    score = factory.LazyFunction(lambda: fake.pyfloat())
    relevant = factory.LazyFunction(lambda: fake.word())
    truth = factory.LazyFunction(lambda: fake.sentence())
