import random

import factory
from faker import Faker

from officers.models import Officer

fake = Faker()

RACES = ['white', 'black']
GENDERS = ['male', 'female']


class OfficerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Officer

    uid = factory.LazyFunction(lambda: fake.uuid4())
    last_name = factory.LazyFunction(lambda: fake.last_name())
    middle_name = factory.LazyFunction(lambda: fake.word())
    first_name = factory.LazyFunction(lambda: fake.first_name())
    birth_year = factory.LazyFunction(lambda: fake.year())
    birth_month = factory.LazyFunction(lambda: fake.month())
    birth_day = factory.LazyFunction(lambda: fake.day_of_month())
    race = factory.LazyFunction(lambda: random.choice(RACES))
    sex = factory.LazyFunction(lambda: random.choice(GENDERS))
    is_name_changed = factory.LazyFunction(lambda: fake.boolean())
    complaint_fraction = factory.LazyFunction(lambda: fake.pyfloat(min_value=0, max_value=1))
