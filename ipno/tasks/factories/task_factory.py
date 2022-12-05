import factory
from faker import Faker

from tasks.constants import TASK_TYPES
from tasks.models import Task

fake = Faker()


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    task_name = factory.LazyFunction(lambda: fake.word())
    command = factory.LazyFunction(lambda: fake.sentence())
    task_type = factory.Faker(
        "random_element", elements=[type[0] for type in TASK_TYPES]
    )
    should_run = factory.LazyFunction(lambda: fake.boolean())
