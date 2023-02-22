from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from mock import patch


class SchemaViewTestCase(APITestCase):
    @patch("schemas.views.validate_schemas")
    def test_validate_schemas(self, validate_schemas_mock):
        response = self.client.post(reverse("validate_schemas"))

        assert response.status_code == status.HTTP_200_OK
        validate_schemas_mock.assert_called()
