from django.utils.text import slugify

import factory
from faker import Faker

from departments.models import Department

fake = Faker()


class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Department

    agency_name = factory.Sequence(lambda n: f"{fake.city()}{n}")
    agency_slug = factory.LazyAttribute(lambda d: slugify(d.agency_name))
    address = factory.LazyFunction(lambda: fake.address())
    phone = factory.LazyFunction(lambda: fake.phone_number())
    location = factory.LazyFunction(
        lambda: (float(fake.latitude()), float(fake.longitude()))
    )
    officer_fraction = factory.LazyFunction(
        lambda: fake.pyfloat(min_value=0, max_value=1)
    )
