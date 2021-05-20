from datetime import datetime

from django.utils.text import slugify

import factory
from faker import Faker

from departments.models import Department

fake = Faker()


class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Department

    name = factory.LazyFunction(lambda: f"{fake.city()} {datetime.utcnow().strftime('%H:%M:%S')} PD")
    slug = factory.LazyAttribute(lambda d: slugify(d.name))
