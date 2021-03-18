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
    middle_initial = factory.LazyFunction(lambda: fake.word())
    first_name = factory.LazyFunction(lambda: fake.first_name())
    employee_id = factory.LazyFunction(lambda: fake.uuid4())
    birth_year = factory.LazyFunction(lambda: fake.year())
    birth_month = factory.LazyFunction(lambda: fake.month())
    birth_day = factory.LazyFunction(lambda: fake.day_of_month())
    race = factory.LazyFunction(lambda: random.choice(RACES))
    gender = factory.LazyFunction(lambda: random.choice(GENDERS))
