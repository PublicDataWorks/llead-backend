import factory
from faker import Faker

from officers.factories import OfficerFactory
from people.models import Person

fake = Faker()


class PersonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Person

    person_id = factory.LazyFunction(lambda: fake.pyint())
    canonical_officer = factory.SubFactory(OfficerFactory)
