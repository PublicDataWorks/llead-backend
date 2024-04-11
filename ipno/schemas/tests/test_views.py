from io import BytesIO
from unittest.mock import patch

from django.urls import reverse

from rest_framework import status

from test_utils.auth_api_test_case import AuthAPITestCase


class SchemaViewTestCase(AuthAPITestCase):
    @patch("schemas.views.GoogleCloudService")
    @patch("schemas.views.open")
    def test_get_schema(self, mock_open, mock_google_cloud_service):
        mock_google_cloud_service.return_value.download_schema.return_value = "schema.sql"
        mock_open.return_value = BytesIO(b"data")

        url = reverse("validate_schemas")
        response = self.auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert b"".join(response.streaming_content) == b"data"
        mock_open.assert_called_once_with("schema.sql", "rb")

    def test_get_schema_unauthorized(self):
        url = reverse("validate_schemas")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
