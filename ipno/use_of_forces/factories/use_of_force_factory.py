import random

import factory
from faker import Faker

from use_of_forces.models import UseOfForce
from officers.factories import OfficerFactory
from departments.factories import DepartmentFactory

fake = Faker()

RACES = ['white', 'black']
GENDERS = ['male', 'female']
YES_NO_CHOICES = ['yes', 'no', None]


class UseOfForceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UseOfForce

    officer = factory.SubFactory(OfficerFactory)
    department = factory.SubFactory(DepartmentFactory)
    uof_uid = factory.LazyFunction(lambda: fake.uuid4())
    uof_tracking_number = factory.LazyFunction(
        lambda: f'{random.randint(1000, 9999)}-{random.randint(100, 999)}'
    )
    report_year = factory.LazyFunction(lambda: int(fake.year()))
    force_description = factory.LazyFunction(lambda: fake.sentence(nb_words=3))
    force_reason = factory.LazyFunction(lambda: fake.word())
    disposition = factory.LazyFunction(lambda: fake.word())
    service_type = factory.LazyFunction(lambda: fake.word())
    citizen_involvement = factory.LazyFunction(lambda: fake.word())
    citizen_age = factory.LazyFunction(lambda: fake.pyint(max_value=100))
    citizen_race = factory.LazyFunction(lambda: random.choice(RACES))
    citizen_sex = factory.LazyFunction(lambda: random.choice(GENDERS))
    citizen_arrested = factory.LazyFunction(lambda: random.choice(YES_NO_CHOICES))
    citizen_injured = factory.LazyFunction(lambda: random.choice(YES_NO_CHOICES))
    citizen_hospitalized = factory.LazyFunction(lambda: random.choice(YES_NO_CHOICES))
    officer_injured = factory.LazyFunction(lambda: random.choice(YES_NO_CHOICES))
    traffic_stop = factory.LazyFunction(lambda: random.choice(YES_NO_CHOICES))
    data_production_year = factory.LazyFunction(lambda: int(fake.year()))
