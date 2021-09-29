import factory
import pytz
from faker import Faker

from tasks.models import TaskLog

fake = Faker()


class TaskLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TaskLog

    finished_at = factory.LazyFunction(lambda: fake.date_time(tzinfo=pytz.utc))
    error_message = factory.LazyFunction(lambda: fake.sentence())
