import random

import factory
from faker import Faker

from documents.models import Document

fake = Faker()


class DocumentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Document
        django_get_or_create = ('docid', 'hrg_no', 'matched_uid')

    docid = factory.LazyFunction(lambda: fake.uuid4())
    hrg_no = factory.LazyFunction(lambda: random.randint(1, 5))
    matched_uid = factory.LazyFunction(lambda: fake.uuid4())
    pdf_db_path = factory.LazyFunction(lambda: fake.file_path(extension='pdf'))
    pdf_db_content_hash = factory.LazyFunction(lambda: fake.md5())
    txt_db_id = factory.LazyFunction(lambda: fake.uuid4())
    txt_db_content_hash = factory.LazyFunction(lambda: fake.md5())
    title = factory.LazyFunction(lambda: fake.sentence())
    document_type = factory.LazyFunction(lambda: fake.file_extension())
    url = factory.LazyFunction(lambda: fake.file_path(extension='pdf'))
    preview_image_url = factory.LazyFunction(lambda: fake.file_path(extension='jpg'))
    incident_date = factory.LazyFunction(lambda: fake.date_object())
    pages_count = factory.LazyFunction(lambda: random.randint(1, 20))
    text_content = factory.LazyFunction(lambda: fake.sentence())
