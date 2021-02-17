import factory
from faker import Faker

from departments.models import WrglFile
from departments.factories.department_factory import DepartmentFactory

fake = Faker()


class WrglFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WrglFile

    name = factory.LazyFunction(lambda: fake.sentence())
    description = factory.LazyFunction(lambda: fake.sentence())
    slug = factory.LazyFunction(lambda: fake.slug())
    url = factory.LazyFunction(lambda: fake.uri())
    download_url = factory.LazyFunction(lambda: fake.file_path(extension='csv'))

    department = factory.SubFactory(DepartmentFactory)
