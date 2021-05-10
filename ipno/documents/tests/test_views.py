from datetime import date

from django.urls import reverse

from rest_framework import status

from documents.factories import DocumentFactory
from departments.factories import DepartmentFactory
from test_utils.auth_api_test_case import AuthAPITestCase


class DocumentsViewSetTestCase(AuthAPITestCase):
    def test_list_success(self):
        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()

        document_1 = DocumentFactory(incident_date=date(2020, 5, 4))
        document_2 = DocumentFactory(incident_date=date(2019, 12, 5))
        document_3 = DocumentFactory()
        document_1.departments.add(department_1)
        document_2.departments.add(department_2)

        response = self.auth_client.get(reverse('api:documents-list'))
        assert response.status_code == status.HTTP_200_OK

        expected_data = [
            {
                'id': document_3.id,
                'document_type': document_3.document_type,
                'title': document_3.title,
                'url': document_3.url,
                'preview_image_url': document_3.preview_image_url,
                'incident_date': str(document_3.incident_date),
                'pages_count': document_3.pages_count,
                'departments': [],
            },
            {
                'id': document_2.id,
                'document_type': document_2.document_type,
                'title': document_2.title,
                'url': document_2.url,
                'preview_image_url': document_2.preview_image_url,
                'incident_date': str(document_2.incident_date),
                'pages_count': document_2.pages_count,
                'departments': [
                    {
                        'id': department_2.slug,
                        'name': department_2.name,
                    }
                ],
            },
            {
                'id': document_1.id,
                'document_type': document_1.document_type,
                'title': document_1.title,
                'url': document_1.url,
                'preview_image_url': document_1.preview_image_url,
                'incident_date': str(document_1.incident_date),
                'pages_count': document_1.pages_count,
                'departments': [
                    {
                        'id': department_1.slug,
                        'name': department_1.name,
                    }
                ],
            }
        ]

        assert response.data == expected_data

    def test_list_unauthorized(self):
        response = self.client.get(reverse('api:documents-list'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
