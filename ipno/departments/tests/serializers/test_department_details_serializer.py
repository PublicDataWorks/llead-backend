from datetime import date

from django.test import TestCase

from departments.serializers import DepartmentDetailsSerializer
from departments.factories import DepartmentFactory, WrglFileFactory
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
            end_date=date(2021, 2, 3),
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
        OfficerHistoryFactory(
            department=other_department,
            officer=officer_1,
            start_date=date(2017, 2, 3),
            end_date=date(2018, 2, 1),
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
        document_7.officers.add(officer_2, officer_3)
        document_1.departments.add(department)
        document_6.departments.add(department)

        complaint_1 = ComplaintFactory(incident_date=date(2020, 5, 4))
        complaint_2 = ComplaintFactory(incident_date=date(2017, 12, 5))
        complaint_3 = ComplaintFactory(incident_date=date(2019, 11, 6))
        complaint_4 = ComplaintFactory(incident_date=date(2018, 8, 9))
        complaint_5 = ComplaintFactory(incident_date=date(2018, 8, 9))
        complaint_6 = ComplaintFactory(incident_date=None)
        complaint_7 = ComplaintFactory(incident_date=None)
        complaint_8 = ComplaintFactory(incident_date=None)
        complaint_1.officers.add(officer_1)
        complaint_2.officers.add(officer_1)
        complaint_3.officers.add(officer_1)
        complaint_4.officers.add(officer_3)
        complaint_6.officers.add(officer_2, officer_3)
        complaint_7.departments.add(department)
        complaint_8.departments.add(department)
        complaint_1.departments.add(department)
        complaint_5.departments.add(department)

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
            'complaints_count': 6,
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

        OfficerHistoryFactory(
            department=department,
            start_date=date(2018, 2, 3),
            end_date=date(2019, 2, 3),
        )
        OfficerHistoryFactory(
            department=department,
            start_date=date(2020, 4, 5),
            end_date=date(2020, 10, 5),
        )
        OfficerHistoryFactory(
            department=department,
            start_date=date(2012, 2, 3),
            end_date=date(2015, 2, 3),
        )
        OfficerHistoryFactory(
            department=department,
            start_date=date(2014, 5, 6),
            end_date=date(2016, 5, 6),
        )
        OfficerHistoryFactory(
            department=department,
            start_date=date(2016, 3, 8),
            end_date=None,
        )
        OfficerHistoryFactory(
            department=department,
            start_date=None,
            end_date=None,
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
            '2012-2016',
            '2018-2021',
        ]

    def test_data_period_with_empty_data(self):
        department = DepartmentFactory()

        result = DepartmentDetailsSerializer(department).data
        assert result['data_period'] == []
