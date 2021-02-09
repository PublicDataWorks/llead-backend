from datetime import date

from django.test import TestCase

from departments.serializers import DepartmentDetailsSerializer
from departments.factories import DepartmentFactory
from officers.factories import OfficerFactory, OfficerHistoryFactory
from documents.factories import DocumentFactory
from complaints.factories import ComplaintFactory


class DepartmentDetailsSerializerTestCase(TestCase):
    def test_data(self):
        department = DepartmentFactory()
        other_department = DepartmentFactory()

        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        officer_3 = OfficerFactory()

        OfficerHistoryFactory(
            department=department,
            officer=officer_1,
            start_date=date(2018, 2, 3),
            end_date=None
        )
        OfficerHistoryFactory(
            department=other_department,
            officer=officer_1,
            start_date=date(2017, 2, 3),
            end_date=date(2018, 2, 1),
        )
        OfficerHistoryFactory(
            department=department,
            officer=officer_2,
            start_date=date(2018, 4, 5),
            end_date=date(2019, 4, 5),
        )
        OfficerHistoryFactory(
            department=department,
            officer=officer_3,
            start_date=date(2018, 4, 5),
            end_date=date(2019, 4, 5),
        )

        document_1 = DocumentFactory(incident_date=date(2020, 5, 4))
        document_2 = DocumentFactory(incident_date=date(2017, 12, 5))
        document_3 = DocumentFactory(incident_date=date(2019, 11, 6))
        document_4 = DocumentFactory(incident_date=date(2018, 8, 9))
        document_5 = DocumentFactory(incident_date=date(2018, 8, 9))
        document_6 = DocumentFactory(incident_date=date(2018, 8, 10))
        document_7 = DocumentFactory(incident_date=None)
        document_1.officers.add(officer_1)
        document_2.officers.add(officer_1)
        document_3.officers.add(officer_1)
        document_4.officers.add(officer_3)
        document_5.officers.add(officer_3)
        document_6.officers.add(officer_3)
        document_7.officers.add(officer_2, officer_3)

        complaint_1 = ComplaintFactory(incident_date=date(2020, 5, 4))
        complaint_2 = ComplaintFactory(incident_date=date(2017, 12, 5))
        complaint_3 = ComplaintFactory(incident_date=date(2019, 11, 6))
        complaint_4 = ComplaintFactory(incident_date=date(2018, 8, 9))
        complaint_5 = ComplaintFactory(incident_date=date(2018, 8, 9))
        complaint_6 = ComplaintFactory(incident_date=None)
        complaint_1.officers.add(officer_1)
        complaint_2.officers.add(officer_1)
        complaint_3.officers.add(officer_1)
        complaint_4.officers.add(officer_3)
        complaint_5.officers.add(officer_3)
        complaint_6.officers.add(officer_2, officer_3)

        result = DepartmentDetailsSerializer(department).data
        assert result == {
            'id': department.id,
            'name': department.name,
            'city': department.city,
            'parish': department.parish,
            'location_map_url': department.location_map_url,
            'officers_count': 3,
            'complaints_count': 4,
            'documents_count': 5,
        }
