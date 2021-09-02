import factory
from faker import Faker

from news_articles.models import CrawlerError

fake = Faker()


class CrawlerErrorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CrawlerError

    response_url = factory.LazyFunction(lambda: fake.uri())
    response_status_code = factory.LazyFunction(lambda: fake.word())
    error_message = factory.LazyFunction(lambda: fake.sentence())
