from django.test.testcases import TestCase

from complaints.factories import ComplaintFactory
from officers.factories import OfficerFactory
from people.factories import PersonFactory
from people.models import Person
from utils.count_complaints import count_complaints


class CountComplaintsTestCase(TestCase):
    def test_update_count_complaints(self):
        person_1 = PersonFactory()
        person_2 = PersonFactory()

        officer_1 = OfficerFactory(person=person_1)
        officer_2 = OfficerFactory(person=person_2)
        officer_3 = OfficerFactory(person=person_2)

        person_1.canonical_officer = officer_1
        person_1.officers.add(officer_1)
        person_2.canonical_officer = officer_2
        person_2.officers.add(officer_2)
        person_2.officers.add(officer_3)

        ComplaintFactory()
        complaint_1 = ComplaintFactory()
        complaint_1.officers.add(officer_2)
        complaint_1.officers.add(officer_3)
        complaint_1.save()
        complaint_2 = ComplaintFactory()
        complaint_2.officers.add(officer_3)

        count_complaints()

        people = Person.objects.all()

        assert people.count() == 2
        assert people.first().all_complaints_count == 0
        assert people.last().all_complaints_count == 2
