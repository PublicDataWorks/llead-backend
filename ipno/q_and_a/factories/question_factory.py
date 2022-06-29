import factory
from faker import Faker
from factory.django import DjangoModelFactory

from q_and_a.factories.section_factory import SectionFactory
from q_and_a.models import Question

fake = Faker()


class QuestionFactory(DjangoModelFactory):
    class Meta:
        model = Question

    question = factory.LazyFunction(lambda: fake.sentence())
    answer = factory.LazyFunction(lambda: fake.sentence())

    section = factory.SubFactory(SectionFactory)
