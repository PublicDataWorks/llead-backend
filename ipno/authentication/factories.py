import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from factory import LazyFunction, LazyAttribute
from faker import Faker

fake = Faker()

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    class Params:
        raw_password = LazyFunction(fake.password)

    password = LazyAttribute(lambda a: make_password(a.raw_password))
