import factory
from faker import Faker

from citizens.models import Citizen

fake = Faker()


class CitizenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Citizen

    citizen_uid = factory.LazyFunction(lambda: fake.uuid4())
    allegation_uid = factory.LazyFunction(lambda: fake.uuid4())
    uof_uid = factory.LazyFunction(lambda: fake.uuid4())
    citizen_influencing_factors = factory.LazyFunction(lambda: fake.word())
    citizen_arrested = factory.LazyFunction(lambda: fake.word())
    citizen_hospitalized = factory.LazyFunction(lambda: fake.word())
    citizen_injured = factory.LazyFunction(lambda: fake.word())
    citizen_age = factory.LazyFunction(lambda: fake.pyint())
    citizen_race = factory.LazyFunction(lambda: fake.word())
    citizen_sex = factory.LazyFunction(lambda: fake.word())
