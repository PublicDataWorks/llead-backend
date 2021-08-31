import factory
from faker import Faker

from news_articles.models import CrawledPost

fake = Faker()


class CrawledPostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CrawledPost

    name = factory.LazyFunction(lambda: fake.word())
    post_guid = factory.LazyFunction(lambda: fake.uuid4())
