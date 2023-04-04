import factory
from faker import Faker

from appeals.models import Appeal
from departments.factories import DepartmentFactory
from officers.factories import OfficerFactory

fake = Faker()


class AppealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Appeal

    officer = factory.SubFactory(OfficerFactory)
    department = factory.SubFactory(DepartmentFactory)
    appeal_uid = factory.LazyFunction(lambda: fake.uuid4())
    charging_supervisor = factory.LazyFunction(lambda: fake.word())
    appeal_disposition = factory.LazyFunction(lambda: fake.word())
    action_appealed = factory.LazyFunction(lambda: fake.word())
    motions = factory.LazyFunction(lambda: fake.word())
