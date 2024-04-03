import random

import factory
from faker import Faker

from brady.models import Brady
from departments.factories.department_factory import DepartmentFactory
from officers.factories.officer_factory import OfficerFactory

fake = Faker()


class BradyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Brady

    brady_uid = factory.LazyFunction(lambda: fake.uuid4())
    uid = factory.LazyFunction(lambda: fake.uuid4())
    disposition = factory.LazyFunction(lambda: fake.word())
    action = factory.LazyFunction(lambda: fake.word())
    allegation_desc = factory.LazyFunction(lambda: fake.word())
    tracking_id_og = factory.LazyFunction(
        lambda: f"{random.randint(1000, 9999)}-{random.randint(100, 999)}"
    )
    charging_agency = factory.LazyFunction(lambda: fake.word())

    department = factory.SubFactory(DepartmentFactory)
    officer = factory.SubFactory(OfficerFactory)
