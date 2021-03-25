from datetime import date

from django.urls import reverse

from rest_framework import status

from test_utils.auth_api_test_case import AuthAPITestCase
from officers.factories import OfficerFactory, OfficerHistoryFactory
from departments.factories import DepartmentFactory
from documents.factories import DocumentFactory
from complaints.factories import ComplaintFactory


class OfficersViewSetTestCase(AuthAPITestCase):
    def test_list_success(self):
        officer_1 = OfficerFactory(first_name='David', last_name='Jonesworth')
        department = DepartmentFactory()
        OfficerHistoryFactory(
            officer=officer_1,
            badge_no='612',
            start_date=date(2017, 1, 5)
        )
        OfficerHistoryFactory(
            officer=officer_1,
            department=department,
            badge_no='12435',
            start_date=date(2020, 5, 4)
        )
        OfficerHistoryFactory(
            officer=officer_1,
            badge_no=None,
            start_date=date(2015, 7, 20)
        )

        officer_2 = OfficerFactory(first_name='Anthony', last_name='Davis')

        response = self.auth_client.get(reverse('api:officers-list'))
        assert response.status_code == status.HTTP_200_OK

        assert response.data == [
            {
                'id': officer_2.id,
                'name': 'Anthony Davis',
                'badges': [],
                'department': None,
            },
            {
                'id': officer_1.id,
                'name': 'David Jonesworth',
                'badges': ['12435', '612'],
                'department': {
                    'id': department.id,
                    'name': department.name,
                },
            }]

    def test_list_unauthorized(self):
        response = self.client.get(reverse('api:officers-list'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_success(self):
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

        expected_result = {
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

        response = self.auth_client.get(
            reverse('api:officers-detail', kwargs={'pk': officer.id})
        )
        assert response.status_code == status.HTTP_200_OK

        assert response.data == expected_result

    def test_retrieve_not_found(self):
        response = self.auth_client.get(
            reverse('api:officers-detail', kwargs={'pk': 1})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_unauthorized(self):
        response = self.client.get(
            reverse('api:officers-detail', kwargs={'pk': 1})
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_documents_success(self):
        department = DepartmentFactory()
        officer = OfficerFactory(department=department)

        document_1 = DocumentFactory(incident_date=date(2020, 5, 4))
        document_2 = DocumentFactory(incident_date=date(2017, 12, 5))
        document_3 = DocumentFactory(incident_date=date(2019, 11, 6))

        OfficerHistoryFactory(
            department=department,
            officer=officer,
            start_date=date(2018, 2, 3),
            end_date=date(2021, 2, 3)
        )

        document_1.officers.add(officer)
        document_2.officers.add(officer)
        document_3.officers.add(officer)

        expected_results = [{
            'id': document_1.id,
            'document_type': document_1.document_type,
            'title': document_1.title,
            'url': document_1.url,
            'incident_date': str(document_1.incident_date),
            'preview_image_url': document_1.preview_image_url,
            'pages_count': document_1.pages_count,
            'text_content': document_1.text_content,
            'departments': [
                {
                    'id': department.id,
                    'name': department.name
                }
            ]
        }, {
            'id': document_3.id,
            'document_type': document_3.document_type,
            'title': document_3.title,
            'url': document_3.url,
            'incident_date': str(document_3.incident_date),
            'preview_image_url': document_3.preview_image_url,
            'pages_count': document_3.pages_count,
            'text_content': document_3.text_content,
            'departments': [
                {
                    'id': department.id,
                    'name': department.name
                }
            ]
        }, {
            'id': document_2.id,
            'document_type': document_2.document_type,
            'title': document_2.title,
            'url': document_2.url,
            'incident_date': str(document_2.incident_date),
            'preview_image_url': document_2.preview_image_url,
            'pages_count': document_2.pages_count,
            'text_content': document_2.text_content,
            'departments': [
                {
                    'id': department.id,
                    'name': department.name
                }
            ]
        }]

        response = self.auth_client.get(
            reverse('api:officers-documents', kwargs={'pk': officer.id})
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_results

    def test_documents_not_found(self):
        response = self.auth_client.get(
            reverse('api:officers-documents', kwargs={'pk': 1})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_documents_unauthorized(self):
        response = self.client.get(
            reverse('api:officers-documents', kwargs={'pk': 1})
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
