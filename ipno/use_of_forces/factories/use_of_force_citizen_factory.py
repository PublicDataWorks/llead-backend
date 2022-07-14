import factory
from faker import Faker

from use_of_forces.models import UseOfForceCitizen

fake = Faker()


class UseOfForceCitizenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UseOfForceCitizen

    uof_citizen_uid = factory.LazyFunction(lambda: fake.uuid4())
    uof_uid = factory.LazyFunction(lambda: fake.uuid4())
    citizen_influencing_factors = factory.LazyFunction(lambda: fake.word())
    citizen_distance_from_officer = factory.LazyFunction(lambda: fake.word())
    citizen_arrested = factory.LazyFunction(lambda: fake.word())
    citizen_arrest_charges = factory.LazyFunction(lambda: fake.word())
    citizen_hospitalized = factory.LazyFunction(lambda: fake.word())
    citizen_injured = factory.LazyFunction(lambda: fake.word())
    citizen_age = factory.LazyFunction(lambda: fake.pyint())
    citizen_race = factory.LazyFunction(lambda: fake.word())
    citizen_sex = factory.LazyFunction(lambda: fake.word())
