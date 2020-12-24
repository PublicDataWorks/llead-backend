import factory
from faker import Faker

from documents.models import Document


fake = Faker()


class DocumentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Document

    title = factory.LazyFunction(lambda: fake.sentence())
