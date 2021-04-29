from datetime import date

from django.test import TestCase

from officers.serializers import OfficerDetailsSerializer
from officers.factories import OfficerFactory, EventFactory
from departments.factories import DepartmentFactory
from documents.factories import DocumentFactory
from complaints.factories import ComplaintFactory
from officers.constants import COMPLAINT_RECEIVE, ALLEGATION_CREATE


class OfficerDetailsSerializerTestCase(TestCase):
    def test_data(self):
        officer = OfficerFactory(
            first_name='David',
            last_name='Jonesworth',
            birth_year=1962,
            race='white',
            gender='male',
        )
        department = DepartmentFactory()
        EventFactory(
            officer=officer,
            department=department,
            badge_no='12435',
            annual_salary='57K',
            year=2020,
            month=5,
            day=4,
        )
        EventFactory(
            officer=officer,
            department=department,
            badge_no='67893',
            annual_salary='20K',
            year=2017,
            month=None,
            day=None,
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
        )
        EventFactory(
            officer=officer,
            kind=ALLEGATION_CREATE,
            badge_no=None,
            year=2020,
            month=5,
            day=4,
        )

        result = OfficerDetailsSerializer(officer).data
        assert result == {
            'id': officer.id,
            'name': 'David Jonesworth',
            'badges': ['12435', '67893', '5432'],
            'birth_year': 1962,
            'race': 'white',
            'gender': 'male',
            'department': {
                'id': department.id,
                'name': department.name,
            },
            'annual_salary': '57K',
            'documents_count': 3,
            'complaints_count': 2,
            'data_period': ['2015-2020'],
            'complaints_data_period': ['2019-2020'],
            'documents_data_period': ['2016-2018'],
        }

    def test_data_period(self):
        officer = OfficerFactory()

        EventFactory(
            officer=officer,
            year=2018,
        )
        EventFactory(
            officer=officer,
            year=2020,
        )
        EventFactory(
            officer=officer,
            year=2012,
        )
        EventFactory(
            officer=officer,
            year=2013,
        )
        EventFactory(
            officer=officer,
            year=2014,
        )
        EventFactory(
            officer=officer,
            year=2019,
        )
        EventFactory(
            officer=officer,
            year=None,
        )

        document_1 = DocumentFactory(incident_date=date(2009, 5, 4))
        document_2 = DocumentFactory(incident_date=date(2018, 1, 6))
        document_1.officers.add(officer)
        document_2.officers.add(officer)

        result = OfficerDetailsSerializer(officer).data
        assert result['data_period'] == [
            '2009',
            '2012-2014',
            '2018-2020',
        ]

    def test_data_period_with_empty_data(self):
        officer = OfficerFactory()

        result = OfficerDetailsSerializer(officer).data
        assert result['data_period'] == []
