import random

import factory
from faker import Faker

from departments.factories import DepartmentFactory
from officers.factories import OfficerFactory
from use_of_forces.models import UseOfForce

fake = Faker()


class UseOfForceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UseOfForce

    department = factory.SubFactory(DepartmentFactory)
    officer = factory.SubFactory(OfficerFactory)
    uof_uid = factory.LazyFunction(lambda: fake.uuid4())
    uid = factory.LazyFunction(lambda: fake.uuid4())
    tracking_id = factory.LazyFunction(
        lambda: f"{random.randint(1000, 9999)}-{random.randint(100, 999)}"
    )
    service_type = factory.LazyFunction(lambda: fake.word())
    disposition = factory.LazyFunction(lambda: fake.word())
    officer_injured = factory.LazyFunction(lambda: fake.word())
    use_of_force_reason = factory.LazyFunction(lambda: fake.word())
    use_of_force_description = factory.LazyFunction(lambda: fake.word())
