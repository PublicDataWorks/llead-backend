from datetime import date

from django.test import TestCase

from departments.serializers import DepartmentDetailsSerializer
from departments.factories import DepartmentFactory, WrglFileFactory
from officers.factories import OfficerFactory, EventFactory
from documents.factories import DocumentFactory
from complaints.factories import ComplaintFactory
from officers.constants import OFFICER_HIRE, OFFICER_LEFT


class DepartmentDetailsSerializerTestCase(TestCase):
    def test_data(self):
        department = DepartmentFactory()
        other_department = DepartmentFactory()

        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        officer_3 = OfficerFactory()
        officer_4 = OfficerFactory()

        EventFactory(
            department=department,
            officer=officer_1,
            kind=OFFICER_HIRE,
            year=2018,
            month=2,
            day=3,
        )

        EventFactory(
            department=department,
            officer=officer_1,
            kind=OFFICER_LEFT,
            year=2021,
            month=2,
            day=3,
        )

        EventFactory(
            department=department,
            officer=officer_2,
            kind=OFFICER_HIRE,
            year=2018,
            month=4,
            day=5,
        )

        EventFactory(
            department=department,
            officer=officer_2,
            kind=OFFICER_LEFT,
            year=2019,
            month=4,
            day=5,
        )

        EventFactory(
            department=department,
            officer=officer_3,
            kind=OFFICER_HIRE,
            year=2018,
            month=5,
            day=8,
        )

        EventFactory(
            department=other_department,
            officer=officer_1,
            kind=OFFICER_HIRE,
            year=2017,
            month=2,
            day=3,
        )

        EventFactory(
            department=other_department,
            officer=officer_4,
            kind=OFFICER_HIRE,
            year=2017,
            month=2,
            day=3,
        )

        documents = DocumentFactory.create_batch(5, incident_date=date(2020, 5, 4))
        DocumentFactory(incident_date=date(2018, 8, 10))
        for document in documents:
            document.departments.add(department)

        complaints = ComplaintFactory.create_batch(2, incident_date=date(2018, 3, 6))
        ComplaintFactory(incident_date=date(2018, 3, 6))
        for complaint in complaints:
            complaint.departments.add(department)

        wrgl_file_1 = WrglFileFactory(department=department, position=2)
        wrgl_file_2 = WrglFileFactory(department=department, position=1)

        result = DepartmentDetailsSerializer(department).data
        assert result == {
            'id': department.id,
            'name': department.name,
            'city': department.city,
            'parish': department.parish,
            'location_map_url': department.location_map_url,
            'officers_count': 3,
            'complaints_count': 2,
            'documents_count': 5,
            'wrgl_files': [
                {
                    'id': wrgl_file_2.id,
                    'name': wrgl_file_2.name,
                    'slug': wrgl_file_2.slug,
                    'description': wrgl_file_2.description,
                    'url': wrgl_file_2.url,
                    'download_url': wrgl_file_2.download_url,
                    'default_expanded': wrgl_file_2.default_expanded,
                },
                {
                    'id': wrgl_file_1.id,
                    'name': wrgl_file_1.name,
                    'slug': wrgl_file_1.slug,
                    'description': wrgl_file_1.description,
                    'url': wrgl_file_1.url,
                    'download_url': wrgl_file_1.download_url,
                    'default_expanded': wrgl_file_1.default_expanded,
                }
            ],
            'data_period': ['2018-2021'],
        }

    def test_data_period(self):
        department = DepartmentFactory()

        EventFactory(
            department=department,
            year=2016,
        )

        EventFactory(
            department=department,
            year=2012,
        )

        EventFactory(
            department=department,
            year=2013,
        )

        EventFactory(
            department=department,
            year=2014,
        )

        EventFactory(
            department=department,
            year=2020,
        )
        EventFactory(
            department=department,
            year=None,
        )

        document_1 = DocumentFactory(incident_date=date(2009, 5, 4))
        document_2 = DocumentFactory(incident_date=date(2018, 1, 6))
        document_1.departments.add(department)
        document_2.departments.add(department)

        complaint_1 = ComplaintFactory(incident_date=date(2019, 7, 2))
        complaint_2 = ComplaintFactory(incident_date=date(2021, 5, 4))
        complaint_1.departments.add(department)
        complaint_2.departments.add(department)

        result = DepartmentDetailsSerializer(department).data
        assert result['data_period'] == [
            '2009',
            '2012-2014',
            '2016',
            '2018-2021',
        ]

    def test_data_period_with_empty_data(self):
        department = DepartmentFactory()

        result = DepartmentDetailsSerializer(department).data
        assert result['data_period'] == []
