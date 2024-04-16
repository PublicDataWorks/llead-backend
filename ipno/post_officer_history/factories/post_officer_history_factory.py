import factory
import pytz
from faker import Faker

from departments.factories.department_factory import DepartmentFactory
from officers.factories.officer_factory import OfficerFactory
from post_officer_history.models.post_officer_history import PostOfficerHistory

fake = Faker()


class PostOfficerHistoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PostOfficerHistory

    uid = factory.LazyFunction(lambda: fake.uuid4())
    history_id = factory.LazyFunction(lambda: fake.uuid4())
    agency = factory.LazyFunction(lambda: fake.word())
    left_reason = factory.LazyFunction(lambda: fake.sentence())
    hire_date = factory.LazyFunction(lambda: fake.date_time(tzinfo=pytz.utc))
    officer = factory.SubFactory(OfficerFactory)
    department = factory.SubFactory(DepartmentFactory)
