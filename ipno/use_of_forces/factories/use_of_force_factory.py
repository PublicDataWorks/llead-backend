import random

import factory
from faker import Faker

from departments.factories import DepartmentFactory
from use_of_forces.models import UseOfForce

fake = Faker()


class UseOfForceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UseOfForce

    department = factory.SubFactory(DepartmentFactory)
    uof_uid = factory.LazyFunction(lambda: fake.uuid4())
    tracking_id = factory.LazyFunction(
        lambda: f"{random.randint(1000, 9999)}-{random.randint(100, 999)}"
    )
    investigation_status = factory.LazyFunction(lambda: fake.word())
    service_type = factory.LazyFunction(lambda: fake.word())
    light_condition = factory.LazyFunction(lambda: fake.word())
    weather_condition = factory.LazyFunction(lambda: fake.word())
    shift_time = factory.LazyFunction(lambda: fake.word())
    disposition = factory.LazyFunction(lambda: fake.word())
    division = factory.LazyFunction(lambda: fake.word())
    division_level = factory.LazyFunction(lambda: fake.word())
    unit = factory.LazyFunction(lambda: fake.word())
    originating_bureau = factory.LazyFunction(lambda: fake.word())
    use_of_force_reason = factory.LazyFunction(lambda: fake.word())
