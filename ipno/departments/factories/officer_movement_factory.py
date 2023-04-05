import factory
from faker import Faker

from departments.models import OfficerMovement

fake = Faker()


class OfficerMovementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OfficerMovement

    date = factory.LazyFunction(lambda: fake.date_object())
    left_reason = factory.LazyFunction(lambda: fake.word())
