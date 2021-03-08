import random

import factory
from faker import Faker

from documents.models import Document

fake = Faker()


class DocumentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Document

    title = factory.LazyFunction(lambda: fake.sentence())
    document_type = factory.LazyFunction(lambda: fake.file_extension())
    url = factory.LazyFunction(lambda: fake.file_path(extension='pdf'))
    preview_image_url = factory.LazyFunction(lambda: fake.file_path(extension='jpg'))
    incident_date = factory.LazyFunction(lambda: fake.date_object())
    pages_count = factory.LazyFunction(lambda: random.randint(1, 20))
    text_content = factory.LazyFunction(lambda: fake.sentence())
