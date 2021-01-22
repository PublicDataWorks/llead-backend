from django.urls import reverse

from rest_framework import status

from documents.factories import DocumentFactory
from test_utils.auth_api_test_case import AuthAPITestCase


class DocumentsViewSetTestCase(AuthAPITestCase):
    def test_retrieve_success(self):
        document = DocumentFactory()

        response = self.auth_client.get(reverse('api:documents-detail', kwargs={'pk': document.id}))
        assert response.status_code == status.HTTP_200_OK

        assert response.data == {
            'id': document.id,
            'title': document.title,
        }

    def test_retrieve_unauthorized(self):
        document = DocumentFactory()

        response = self.client.get(reverse('api:documents-detail', kwargs={'pk': document.id}))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
