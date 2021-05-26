import random

import factory
from faker import Faker

from officers.models import Event
from officers.factories.officer_factory import OfficerFactory
from departments.factories import DepartmentFactory
from officers.constants import EVENT_KINDS

fake = Faker()


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    event_uid = factory.LazyFunction(lambda: fake.uuid4())
    officer = factory.SubFactory(OfficerFactory)
    department = factory.SubFactory(DepartmentFactory)
    kind = factory.LazyFunction(lambda: random.choice(EVENT_KINDS))
    year = factory.LazyFunction(lambda: int(fake.year()))
    month = factory.LazyFunction(lambda: int(fake.month()))
    day = factory.LazyFunction(lambda: int(fake.day_of_month()))
