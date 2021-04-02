import random

import factory
from faker import Faker

from complaints.models import Complaint

fake = Faker()


class ComplaintFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Complaint

    incident_date = factory.LazyFunction(lambda: fake.date_object())
    occur_year = factory.LazyFunction(lambda: int(fake.year()))
    occur_month = factory.LazyFunction(lambda: int(fake.month()))
    occur_day = factory.LazyFunction(lambda: int(fake.day_of_month()))
    rule_violation = factory.LazyFunction(lambda: fake.sentence(nb_words=3))
    paragraph_violation = factory.LazyFunction(lambda: fake.sentence(nb_words=3))
    disposition = factory.LazyFunction(lambda: fake.word())
    action = factory.LazyFunction(lambda: fake.word())
    tracking_number = factory.LazyFunction(
        lambda: f'{random.randint(1000, 9999)}-{random.randint(100, 999)}'
    )
