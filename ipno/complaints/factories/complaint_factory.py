import random

import factory
from faker import Faker

from complaints.models import Complaint

fake = Faker()


class ComplaintFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Complaint

    uid = factory.LazyFunction(lambda: str(random.randint(100000, 999999)))
    incident_date = factory.LazyFunction(lambda: fake.date())
