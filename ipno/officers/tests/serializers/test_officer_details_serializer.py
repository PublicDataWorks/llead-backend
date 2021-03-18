from datetime import date

from django.test import TestCase

from officers.serializers import OfficerDetailsSerializer
from officers.factories import OfficerFactory, OfficerHistoryFactory
from departments.factories import DepartmentFactory
from documents.factories import DocumentFactory
from complaints.factories import ComplaintFactory


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
        OfficerHistoryFactory(
            officer=officer,
            department=department,
            badge_no='12435',
            annual_salary='57K',
            start_date=date(2020, 5, 4),
            end_date=date(2021, 5, 4)
        )
        OfficerHistoryFactory(
            officer=officer,
            badge_no=None,
            annual_salary='20K',
            start_date=date(2015, 7, 20),
            end_date=date(2020, 5, 4)
        )

        document_1 = DocumentFactory(incident_date=date(2016, 5, 4))
        document_2 = DocumentFactory(incident_date=date(2017, 5, 4))
        document_3 = DocumentFactory(incident_date=date(2018, 5, 4))

        document_1.officers.add(officer)
        document_2.officers.add(officer)
        document_3.officers.add(officer)

        complaint_1 = ComplaintFactory(incident_date=date(2019, 5, 4))
        complaint_2 = ComplaintFactory(incident_date=date(2020, 5, 4))

        complaint_1.officers.add(officer)
        complaint_2.officers.add(officer)

        result = OfficerDetailsSerializer(officer).data
        assert result == {
            'id': officer.id,
            'name': 'David Jonesworth',
            'badges': ['12435'],
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
            'data_period': ['2015-2021'],
            'complaints_data_period': ['2019-2020'],
            'documents_data_period': ['2016-2018'],
        }

    def test_data_period(self):
        officer = OfficerFactory()

        OfficerHistoryFactory(
            officer=officer,
            start_date=date(2018, 2, 3),
            end_date=date(2019, 2, 3),
        )
        OfficerHistoryFactory(
            officer=officer,
            start_date=date(2020, 4, 5),
            end_date=date(2020, 10, 5),
        )
        OfficerHistoryFactory(
            officer=officer,
            start_date=date(2012, 2, 3),
            end_date=date(2015, 2, 3),
        )
        OfficerHistoryFactory(
            officer=officer,
            start_date=date(2014, 5, 6),
            end_date=date(2016, 5, 6),
        )
        OfficerHistoryFactory(
            officer=officer,
            start_date=date(2016, 3, 8),
            end_date=None,
        )
        OfficerHistoryFactory(
            officer=officer,
            start_date=None,
            end_date=None,
        )

        document_1 = DocumentFactory(incident_date=date(2009, 5, 4))
        document_2 = DocumentFactory(incident_date=date(2018, 1, 6))
        document_1.officers.add(officer)
        document_2.officers.add(officer)

        complaint_1 = ComplaintFactory(incident_date=date(2019, 7, 2))
        complaint_2 = ComplaintFactory(incident_date=date(2021, 5, 4))
        complaint_1.officers.add(officer)
        complaint_2.officers.add(officer)

        result = OfficerDetailsSerializer(officer).data
        assert result['data_period'] == [
            '2009',
            '2012-2016',
            '2018-2021',
        ]

    def test_data_period_with_empty_data(self):
        officer = OfficerFactory()

        result = OfficerDetailsSerializer(officer).data
        assert result['data_period'] == []
