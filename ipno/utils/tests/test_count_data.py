from django.test.testcases import TestCase

from complaints.factories import ComplaintFactory
from departments.factories import DepartmentFactory
from officers.factories import OfficerFactory
from people.factories import PersonFactory
from people.models import Person
from utils.count_data import count_complaints, calculate_officer_fraction, calculate_complaint_fraction


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


class CalculateOfficerFractionTestCase(TestCase):
    def test_calculate_officer_fraction(self):
        department_1 = DepartmentFactory(name='Orleans PD')
        department_2 = DepartmentFactory(name='New Orleans PD')
        department_3 = DepartmentFactory(name='New Orleans Parish Sheriff Office')

        department_1_officers = OfficerFactory.create_batch(45)
        department_2_officers = OfficerFactory.create_batch(180)
        department_3_officers = OfficerFactory.create_batch(90)

        person = PersonFactory(canonical_officer=department_1_officers[0])
        for officer in department_1_officers:
            officer.department = department_1
            officer.save()

            person.officers.add(officer)
            person.save()

        for officer in department_2_officers:
            officer.department = department_2
            officer.save()

            person.officers.add(officer)
            person.save()

        for officer in department_3_officers:
            officer.department = department_3
            officer.save()

            person.officers.add(officer)
            person.save()

        calculate_officer_fraction()

        department_1.refresh_from_db()
        department_2.refresh_from_db()
        department_3.refresh_from_db()

        assert department_1.officer_fraction == 0.25
        assert department_2.officer_fraction == 1.0
        assert department_3.officer_fraction == 0.5


class CalculateComplaintFractionTestCase(TestCase):
    def test_calculate_complaint_fraction(self):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        officer_3 = OfficerFactory()

        person_1 = PersonFactory(canonical_officer=officer_1, all_complaints_count=45)
        person_1.officers.add(officer_1)
        person_1.save()
        person_2 = PersonFactory(canonical_officer=officer_2, all_complaints_count=90)
        person_2.officers.add(officer_2)
        person_2.save()
        person_3 = PersonFactory(canonical_officer=officer_3, all_complaints_count=180)
        person_3.officers.add(officer_3)
        person_3.save()

        calculate_complaint_fraction()

        officer_1.refresh_from_db()
        officer_2.refresh_from_db()
        officer_3.refresh_from_db()

        assert officer_1.complaint_fraction == 0.25
        assert officer_2.complaint_fraction == 0.5
        assert officer_3.complaint_fraction == 1.0
