from datetime import date

from django.test import TestCase

from officers.serializers import OfficerDetailsSerializer
from officers.factories import OfficerFactory, EventFactory
from departments.factories import DepartmentFactory
from documents.factories import DocumentFactory
from complaints.factories import ComplaintFactory
from officers.constants import COMPLAINT_RECEIVE, ALLEGATION_CREATE
from people.factories import PersonFactory


class OfficerDetailsSerializerTestCase(TestCase):
    def test_data(self):
        department = DepartmentFactory()

        officer = OfficerFactory(
            first_name='David',
            last_name='Jonesworth',
            birth_year=1962,
            race='white',
            sex='male',
            department=department,
        )
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        EventFactory(
            officer=officer,
            department=department,
            badge_no='12435',
            salary='57000.145',
            salary_freq='yearly',
            year=2020,
            month=5,
            day=4,
        )
        EventFactory(
            officer=officer,
            department=department,
            badge_no='67893',
            salary='20.23',
            salary_freq='hourly',
            year=2017,
            month=6,
            day=5,
        )
        EventFactory(
            officer=officer,
            department=department,
            badge_no='5432',
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            badge_no='12435',
            year=2015,
            month=7,
            day=20,
            department=None
        )

        document_1 = DocumentFactory(incident_date=date(2016, 5, 4))
        document_2 = DocumentFactory(incident_date=date(2017, 5, 4))
        document_3 = DocumentFactory(incident_date=date(2018, 5, 4))

        document_1.officers.add(officer)
        document_2.officers.add(officer)
        document_3.officers.add(officer)

        complaint_1 = ComplaintFactory()
        complaint_2 = ComplaintFactory()

        complaint_1.officers.add(officer)
        complaint_2.officers.add(officer)

        EventFactory(
            officer=officer,
            kind=COMPLAINT_RECEIVE,
            badge_no=None,
            year=2019,
            month=5,
            day=4,
            department=None
        )
        EventFactory(
            officer=officer,
            kind=ALLEGATION_CREATE,
            badge_no=None,
            year=2020,
            month=5,
            day=4,
            department=None
        )
        EventFactory(
            department=department,
            officer=officer,
            rank_desc="junior",
            year=2018,
            month=4,
            day=5,
        )
        EventFactory(
            department=department,
            officer=officer,
            rank_desc="senior",
            year=2020,
            month=4,
            day=5,
        )
        EventFactory(
            department=department,
            officer=officer,
            rank_desc="captain",
            year=2021,
            month=None,
            day=None,
        )

        result = OfficerDetailsSerializer(officer).data
        assert result == {
            'id': officer.id,
            'name': 'David Jonesworth',
            'badges': ['12435', '67893', '5432'],
            'birth_year': 1962,
            'race': 'white',
            'sex': 'male',
            'departments': [{
                'id': department.slug,
                'name': department.name,
            }],
            'salary': '57000.14',
            'salary_freq': 'yearly',
            'documents_count': 3,
            'complaints_count': 2,
            'latest_rank': 'captain',
        }

    def test_salary_fields(self):
        officer = OfficerFactory()
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        EventFactory(
            officer=officer,
            salary='57000.145',
            salary_freq='yearly',
            year=2021,
            month=2,
            day=4,
        )
        EventFactory(
            officer=officer,
            salary=20000.23,
            salary_freq=None,
            year=2020,
            month=1,
            day=2,
        )
        EventFactory(
            officer=officer,
            salary=None,
            salary_freq=None,
            year=2021,
            month=3,
            day=6,
        )

        result = OfficerDetailsSerializer(officer).data
        assert result['salary'] == '57000.14'
        assert result['salary_freq'] == 'yearly'

    def test_salary_fields_with_empty_salary_freq(self):
        officer = OfficerFactory()
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        EventFactory(
            officer=officer,
            salary='57000.122',
            salary_freq=None,
            year=2021,
            month=2,
            day=4,
        )
        EventFactory(
            officer=officer,
            salary='20000.152',
            salary_freq=None,
            year=2020,
            month=1,
            day=2,
        )
        EventFactory(
            officer=officer,
            salary=None,
            salary_freq=None,
            year=2021,
            month=3,
            day=6,
        )

        result = OfficerDetailsSerializer(officer).data
        assert result['salary'] is None
        assert result['salary_freq'] is None

    def test_salary_fields_with_empty_salary(self):
        officer = OfficerFactory()
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        EventFactory(
            officer=officer,
            salary=None,
            salary_freq='yearly',
            year=2021,
            month=2,
            day=4,
        )
        EventFactory(
            officer=officer,
            salary=None,
            salary_freq='monthly',
            year=2020,
            month=1,
            day=2,
        )
        EventFactory(
            officer=officer,
            salary=None,
            salary_freq='hourly',
            year=2021,
            month=3,
            day=6,
        )

        result = OfficerDetailsSerializer(officer).data
        assert result['salary'] is None
        assert result['salary_freq'] is None

    def test_officer_data_without_event(self):
        officer = OfficerFactory(
            first_name='David',
            last_name='Jonesworth',
            birth_year=1962,
            race='white',
            sex='male',
        )
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        document_1 = DocumentFactory(incident_date=date(2016, 5, 4))
        document_2 = DocumentFactory(incident_date=date(2017, 5, 4))
        document_3 = DocumentFactory(incident_date=date(2018, 5, 4))

        document_1.officers.add(officer)
        document_2.officers.add(officer)
        document_3.officers.add(officer)

        complaint_1 = ComplaintFactory()
        complaint_2 = ComplaintFactory()

        complaint_1.officers.add(officer)
        complaint_2.officers.add(officer)

        result = OfficerDetailsSerializer(officer).data
        assert result == {
            'id': officer.id,
            'name': 'David Jonesworth',
            'badges': [],
            'birth_year': 1962,
            'race': 'white',
            'sex': 'male',
            'departments': [],
            'salary': None,
            'salary_freq': None,
            'documents_count': 3,
            'complaints_count': 2,
            'latest_rank': None,
        }

    def test_data_with_related_officer_departments_and_badges(self):
        department = DepartmentFactory()
        related_department = DepartmentFactory()

        officer = OfficerFactory(
            first_name='David',
            last_name='Jonesworth',
            birth_year=1962,
            race='white',
            sex='male',
            department=department,
        )
        person = PersonFactory(canonical_officer=officer)
        related_officer = OfficerFactory(department=related_department)
        person.officers.add(officer)
        person.officers.add(related_officer)
        person.save()

        EventFactory(
            officer=officer,
            department=department,
            badge_no='12435',
            salary='57000.145',
            salary_freq='yearly',
            year=2020,
            month=5,
            day=4,
        )
        EventFactory(
            officer=officer,
            department=department,
            badge_no='67893',
            salary='20.23',
            salary_freq='hourly',
            year=2017,
            month=6,
            day=10,
        )
        EventFactory(
            officer=officer,
            department=department,
            badge_no='5432',
            year=2020,
            month=7,
            day=6,
        )
        EventFactory(
            officer=officer,
            badge_no='12435',
            year=2015,
            month=7,
            day=20,
            department=None
        )
        EventFactory(
            officer=related_officer,
            badge_no='13579',
            year=2021,
            month=7,
            day=20,
            department=related_department
        )

        document_1 = DocumentFactory(incident_date=date(2016, 5, 4))
        document_2 = DocumentFactory(incident_date=date(2017, 5, 4))
        document_3 = DocumentFactory(incident_date=date(2018, 5, 4))

        document_1.officers.add(officer)
        document_2.officers.add(officer)
        document_3.officers.add(officer)

        complaint_1 = ComplaintFactory()
        complaint_2 = ComplaintFactory()

        complaint_1.officers.add(officer)
        complaint_2.officers.add(officer)

        EventFactory(
            officer=officer,
            kind=COMPLAINT_RECEIVE,
            badge_no=None,
            year=2019,
            month=5,
            day=4,
            department=None
        )
        EventFactory(
            officer=officer,
            kind=ALLEGATION_CREATE,
            badge_no=None,
            year=2020,
            month=5,
            day=4,
            department=None
        )

        result = OfficerDetailsSerializer(officer).data
        assert result == {
            'id': officer.id,
            'name': 'David Jonesworth',
            'badges': ['13579', '5432', '12435', '67893'],
            'birth_year': 1962,
            'race': 'white',
            'sex': 'male',
            'departments': [
                {
                    'id': department.slug,
                    'name': department.name,
                },
                {
                    'id': related_department.slug,
                    'name': related_department.name,
                }
            ],
            'salary': '57000.14',
            'salary_freq': 'yearly',
            'documents_count': 3,
            'complaints_count': 2,
            'latest_rank': None,
        }
