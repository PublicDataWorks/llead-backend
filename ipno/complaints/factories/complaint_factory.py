import random

import factory
from faker import Faker

from complaints.models import Complaint

fake = Faker()


class ComplaintFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Complaint

    allegation_uid = factory.LazyFunction(lambda: fake.uuid4())
    uid = factory.LazyFunction(lambda: fake.uuid4())
    disposition = factory.LazyFunction(lambda: fake.word())
    action = factory.LazyFunction(lambda: fake.word())
    allegation = factory.LazyFunction(lambda: fake.word())
    allegation_desc = factory.LazyFunction(lambda: fake.word())
    tracking_id = factory.LazyFunction(
        lambda: f"{random.randint(1000, 9999)}-{random.randint(100, 999)}"
    )
    citizen_arrested = factory.LazyFunction(lambda: fake.word())
    traffic_stop = factory.LazyFunction(lambda: fake.word())
