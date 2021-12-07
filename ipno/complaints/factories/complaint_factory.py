import random

import factory
from faker import Faker

from complaints.models import Complaint

fake = Faker()


class ComplaintFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Complaint

    allegation_uid = factory.LazyFunction(lambda: fake.uuid4())
    rule_code = factory.LazyFunction(lambda: fake.word())
    rule_violation = factory.LazyFunction(lambda: fake.sentence(nb_words=3))
    paragraph_violation = factory.LazyFunction(lambda: fake.sentence(nb_words=3))
    disposition = factory.LazyFunction(lambda: fake.word())
    action = factory.LazyFunction(lambda: fake.word())
    tracking_number = factory.LazyFunction(
        lambda: f'{random.randint(1000, 9999)}-{random.randint(100, 999)}'
    )
