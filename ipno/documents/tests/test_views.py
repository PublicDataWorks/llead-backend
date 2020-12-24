from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from documents.factories import DocumentFactory


class DocumentViewSetTestCase(APITestCase):
    def test_retrieve(self):
        document = DocumentFactory()

        response = self.client.get(reverse('api:documents-detail', kwargs={'pk': document.id}))
        assert response.status_code == status.HTTP_200_OK

        assert response.data == {
            'id': document.id,
            'title': document.title,
        }
