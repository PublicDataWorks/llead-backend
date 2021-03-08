import factory
from faker import Faker

from complaints.models import Complaint

fake = Faker()


class ComplaintFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Complaint

    incident_date = factory.LazyFunction(lambda: fake.date_object())
