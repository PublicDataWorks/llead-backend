import factory
from faker import Faker

from use_of_forces.models import UseOfForceOfficer

fake = Faker()


class UseOfForceOfficerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UseOfForceOfficer

    uof_uid = factory.LazyFunction(lambda: fake.uuid4())
    uid = factory.LazyFunction(lambda: fake.uuid4())
    use_of_force_description = factory.LazyFunction(lambda: fake.word())
    use_of_force_level = factory.LazyFunction(lambda: fake.word())
    use_of_force_effective = factory.LazyFunction(lambda: fake.word())
    age = factory.LazyFunction(lambda: fake.pyint())
    years_of_service = factory.LazyFunction(lambda: fake.pyint())
    officer_injured = factory.LazyFunction(lambda: fake.word())
