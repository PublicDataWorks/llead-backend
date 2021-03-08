from datetime import date
from operator import itemgetter

from django.urls import reverse

from rest_framework import status

from test_utils.auth_api_test_case import AuthAPITestCase
from departments.factories import DepartmentFactory, WrglFileFactory
from officers.factories import OfficerFactory, OfficerHistoryFactory
from documents.factories import DocumentFactory
from complaints.factories import ComplaintFactory
from utils.search_index import rebuild_search_index


class DepartmentsViewSetTestCase(AuthAPITestCase):
    def test_list_success(self):
        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()
        department_3 = DepartmentFactory()

        department_1_officers = OfficerFactory.create_batch(2)
        department_2_officers = OfficerFactory.create_batch(5)

        for officer in department_1_officers:
            officer.departments.add(department_1)

        for officer in department_2_officers:
            officer.departments.add(department_2)

        response = self.auth_client.get(reverse('api:departments-list'))
        assert response.status_code == status.HTTP_200_OK

        assert response.data == [{
            'id': department_2.id,
            'name': department_2.name,
            'city': department_2.city,
            'parish': department_2.parish,
            'location_map_url': department_2.location_map_url,
        }, {
            'id': department_1.id,
            'name': department_1.name,
            'city': department_1.city,
            'parish': department_1.parish,
            'location_map_url': department_1.location_map_url,
        }, {
            'id': department_3.id,
            'name': department_3.name,
            'city': department_3.city,
            'parish': department_3.parish,
            'location_map_url': department_3.location_map_url,
        }]

    def test_list_unauthorized(self):
        response = self.client.get(reverse('api:departments-list'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_success(self):
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

        expected_result = {
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
            'data_period': ['2018-2019'],
        }

        response = self.auth_client.get(
            reverse('api:departments-detail', kwargs={'pk': department.id})
        )
        assert response.status_code == status.HTTP_200_OK

        assert response.data == expected_result

    def test_retrieve_not_found(self):
        response = self.auth_client.get(
            reverse('api:departments-detail', kwargs={'pk': 1})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_unauthorized(self):
        response = self.client.get(
            reverse('api:departments-detail', kwargs={'pk': 1})
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_documents_success(self):
        department = DepartmentFactory()

        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()

        officer_1.departments.add(department)
        officer_2.departments.add(department)

        document_1 = DocumentFactory(incident_date=date(2020, 5, 4))
        document_2 = DocumentFactory(incident_date=date(2017, 12, 5))
        document_3 = DocumentFactory(incident_date=date(2019, 11, 6))
        document_4 = DocumentFactory(incident_date=date(2021, 7, 9))

        OfficerHistoryFactory(
            department=department,
            officer=officer_1,
            start_date=date(2018, 2, 3),
            end_date=date(2021, 2, 3),
        )
        OfficerHistoryFactory(
            department=department,
            officer=officer_2,
            start_date=date(2019, 2, 3),
            end_date=date(2020, 2, 3),
        )

        document_1.officers.add(officer_1)
        document_2.officers.add(officer_1)
        document_3.officers.add(officer_2)
        document_3.departments.add(department)
        document_4.departments.add(department)

        response = self.auth_client.get(
            reverse('api:departments-documents', kwargs={'pk': department.id}),
            {
                'limit': 2,
            }
        )

        expected_results = [{
            'id': document_4.id,
            'document_type': document_4.document_type,
            'title': document_4.title,
            'url': document_4.url,
            'incident_date': str(document_4.incident_date),
            'preview_image_url': document_4.preview_image_url,
            'pages_count': document_4.pages_count,
        }, {
            'id': document_1.id,
            'document_type': document_1.document_type,
            'title': document_1.title,
            'url': document_1.url,
            'incident_date': str(document_1.incident_date),
            'preview_image_url': document_1.preview_image_url,
            'pages_count': document_1.pages_count,
        }]

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
        assert response.data['previous'] is None
        assert response.data['next'] == f'http://testserver/api/departments/{department.id}/documents/?limit=2&offset=2'
        assert response.data['results'] == expected_results

    def test_documents_with_limit_and_offset(self):
        department = DepartmentFactory()

        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()

        officer_1.departments.add(department)
        officer_2.departments.add(department)

        document_1 = DocumentFactory(incident_date=date(2020, 5, 4))
        document_2 = DocumentFactory(incident_date=date(2017, 12, 5))
        document_3 = DocumentFactory(incident_date=date(2019, 11, 6))
        document_4 = DocumentFactory(incident_date=date(2021, 7, 9))

        OfficerHistoryFactory(
            department=department,
            officer=officer_1,
            start_date=date(2018, 2, 3),
            end_date=date(2021, 2, 3),
        )
        OfficerHistoryFactory(
            department=department,
            officer=officer_2,
            start_date=date(2019, 2, 3),
            end_date=date(2020, 2, 3),
        )

        document_1.officers.add(officer_1)
        document_2.officers.add(officer_1)
        document_3.officers.add(officer_2)
        document_3.departments.add(department)
        document_4.departments.add(department)

        response = self.auth_client.get(
            reverse('api:departments-documents', kwargs={'pk': department.id}),
            {
                'limit': 2,
                'offset': 2,
            }
        )

        expected_results = [{
            'id': document_3.id,
            'document_type': document_3.document_type,
            'title': document_3.title,
            'url': document_3.url,
            'incident_date': str(document_3.incident_date),
            'preview_image_url': document_3.preview_image_url,
            'pages_count': document_3.pages_count,
        }]

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
        assert response.data['previous'] == f'http://testserver/api/departments/{department.id}/documents/?limit=2'
        assert response.data['next'] is None
        assert response.data['results'] == expected_results

    def test_search_documents(self):
        department = DepartmentFactory()

        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()

        officer_1.departments.add(department)
        officer_2.departments.add(department)

        document_1 = DocumentFactory(
            title='Document title 1',
            text_content='Text content 1',
            incident_date=date(2020, 5, 4)
        )
        document_2 = DocumentFactory(
            title='Document title keyword2',
            text_content='Text content keyword 2',
            incident_date=date(2017, 12, 5)
        )
        document_3 = DocumentFactory(
            title='Document title keyword3',
            text_content='Text content 3',
            incident_date=date(2019, 11, 6)
        )
        document_4 = DocumentFactory(
            title='Document title 4',
            text_content='Text content keyword 4',
            incident_date=date(2021, 7, 9)
        )

        OfficerHistoryFactory(
            department=department,
            officer=officer_1,
            start_date=date(2018, 2, 3),
            end_date=date(2021, 2, 3),
        )
        OfficerHistoryFactory(
            department=department,
            officer=officer_2,
            start_date=date(2019, 2, 3),
            end_date=date(2020, 2, 3),
        )

        document_1.officers.add(officer_1)
        document_2.officers.add(officer_1)
        document_3.officers.add(officer_2)
        document_3.departments.add(department)
        document_4.departments.add(department)

        rebuild_search_index()

        response = self.auth_client.get(
            reverse('api:departments-documents', kwargs={'pk': department.id}),
            {'q': 'keyword'}
        )

        expected_results = [
            {
                'id': document_3.id,
                'document_type': document_3.document_type,
                'title': document_3.title,
                'url': document_3.url,
                'incident_date': str(document_3.incident_date),
                'text_content': document_3.text_content,
                'text_content_highlight': None,
            }, {
                'id': document_4.id,
                'document_type': document_4.document_type,
                'title': document_4.title,
                'url': document_4.url,
                'incident_date': str(document_4.incident_date),
                'text_content': document_4.text_content,
                'text_content_highlight': 'Text content <em>keyword</em> 4',
            }
        ]

        results = sorted(response.data['results'], key=itemgetter('id'))

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        assert response.data['previous'] is None
        assert response.data['next'] is None
        assert results == expected_results

    def test_documents_not_found(self):
        response = self.auth_client.get(
            reverse('api:departments-documents', kwargs={'pk': 1})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_documents_unauthorized(self):
        response = self.client.get(
            reverse('api:departments-documents', kwargs={'pk': 1})
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
