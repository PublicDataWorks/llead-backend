import factory
from faker import Faker

from news_articles.models import NewsArticle

fake = Faker()


class NewsArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NewsArticle

    source_name = factory.LazyFunction(lambda: fake.word())
    guid = factory.LazyFunction(lambda: fake.uuid4())
    title = factory.LazyFunction(lambda: fake.sentence())
    link = factory.LazyFunction(lambda: fake.uri())
    content = factory.LazyFunction(lambda: fake.sentence())
    published_date = factory.LazyFunction(lambda: fake.date_object())
    author = factory.LazyFunction(lambda: fake.word())
    url = factory.LazyFunction(lambda: fake.uri())
