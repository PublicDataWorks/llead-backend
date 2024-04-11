from django.conf import settings
from django.urls import reverse

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
from rest_framework.test import APITestCase

from mock import patch

from data.constants import IMPORT_TASK_ID_CACHE_KEY


class DataImportViewTestCase(APITestCase):
    def setUp(self):
        self.url = reverse("import_data")

    def test_failed_due_to_invalid_api_key(self):
        response = self.client.post(self.url, {}, **{"HTTP_X_API_KEY": "invalid-key"})

        assert response.status_code == HTTP_403_FORBIDDEN
        assert response.data == {"error": "Invalid API Key"}

    def test_failed_due_to_empty_folder_name(self):
        response = self.client.post(
            self.url, {}, **{"HTTP_X_API_KEY": settings.IPNO_API_KEY}
        )

        assert response.status_code == HTTP_400_BAD_REQUEST
        assert response.data == {"error": "Folder name is required"}

    @patch("data.views.cache")
    @patch("data.views.import_data")
    def test_schedule_task_successfully(self, mock_import_data_task, mock_cache):
        mock_cache.get.return_value = None
        mock_import_data_task.delay.return_value.id = "task_id"

        response = self.client.post(
            self.url,
            {"folder_name": "test_folder"},
            **{"HTTP_X_API_KEY": settings.IPNO_API_KEY},
        )

        mock_import_data_task.delay.assert_called_once_with("test_folder")
        mock_cache.set.assert_called_once_with(IMPORT_TASK_ID_CACHE_KEY, "task_id")
        assert response.data == {"message": "Request received"}
        assert response.status_code == HTTP_200_OK

    @patch("data.views.cache")
    @patch("data.views.import_data")
    def test_does_not_accept_new_request_when_there_is_scheduled_task(
        self, mock_import_data_task, mock_cache
    ):
        mock_import_data_task.delay.return_value.id = "task_id"
        mock_cache.get.return_value = "task_id"

        response = self.client.post(
            self.url,
            {"folder_name": "test_folder"},
            **{"HTTP_X_API_KEY": settings.IPNO_API_KEY},
        )

        mock_import_data_task.delay.assert_not_called()
        mock_cache.set.assert_not_called()

        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
        assert response.data == {
            "error": "Cannot schedule request, there's another task scheduled"
        }
