import random

import factory
from faker import Faker

from officers.models import OfficerHistory
from officers.factories.officer_factory import OfficerFactory
from departments.factories import DepartmentFactory

fake = Faker()


class OfficerHistoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OfficerHistory

    officer = factory.SubFactory(OfficerFactory)
    department = factory.SubFactory(DepartmentFactory)
    start_date = factory.LazyFunction(lambda: fake.date_object())
    badge_no = factory.LazyFunction(lambda: str(random.randint(10000, 99999)))
