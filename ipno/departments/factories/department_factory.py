import factory
from faker import Faker

from departments.models import Department

fake = Faker()


class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Department

    name = factory.LazyFunction(lambda: f"{fake.city()} Department")
