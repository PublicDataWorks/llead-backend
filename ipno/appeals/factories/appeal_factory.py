import random

import factory
from faker import Faker

from appeals.models import Appeal
from officers.factories import OfficerFactory
from departments.factories import DepartmentFactory

fake = Faker()


class AppealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Appeal

    officer = factory.SubFactory(OfficerFactory)
    department = factory.SubFactory(DepartmentFactory)
    appeal_uid = factory.LazyFunction(lambda: fake.uuid4())
    docket_no = factory.LazyFunction(lambda: f'{random.randint(00, 99)}-{random.randint(00, 99)}')
    counsel = factory.LazyFunction(lambda: fake.word())
    charging_supervisor = factory.LazyFunction(lambda: fake.word())
    appeal_disposition = factory.LazyFunction(lambda: fake.word())
    action_appealed = factory.LazyFunction(lambda: fake.word())
    appealed = factory.LazyFunction(lambda: fake.word())
    motions = factory.LazyFunction(lambda: fake.word())
