import factory
from faker import Faker

from departments.factories import DepartmentFactory
from departments.models import OfficerMovement
from officers.factories import OfficerFactory

fake = Faker()


class OfficerMovementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OfficerMovement

    start_department = factory.SubFactory(DepartmentFactory)
    end_department = factory.SubFactory(DepartmentFactory)
    officer = factory.SubFactory(OfficerFactory)
    date = factory.LazyFunction(lambda: fake.date_object())
    left_reason = factory.LazyFunction(lambda: fake.word())
