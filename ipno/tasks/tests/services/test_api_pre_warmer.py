from django.test import TestCase, override_settings

from mock import patch

from departments.factories import DepartmentFactory
from tasks.services import APIPreWarmer


class APIPreWarmerTestCase(TestCase):
    @patch("tasks.services.api_pre_warmer.requests.get")
    @override_settings(SERVER_URL="http://web:8000")
    def test_pre_warm_front_page_api_successfully(self, mock_request_get):
        mock_request_get.return_value.status_code = 200
        mock_request_get.return_value.json.return_value = "mock response"

        api_pre_warmer = APIPreWarmer()
        pre_warming_errors = api_pre_warmer.pre_warm_front_page_api()

        assert len(pre_warming_errors) == 0

    @patch("tasks.services.api_pre_warmer.requests.get")
    @override_settings(SERVER_URL="http://web:8000")
    def test_pre_warm_front_page_api_fail(self, mock_request_get):
        mock_request_get.side_effect = Exception()

        api_pre_warmer = APIPreWarmer()
        pre_warming_errors = api_pre_warmer.pre_warm_front_page_api()

        assert len(pre_warming_errors) > 0

    @patch("tasks.services.api_pre_warmer.requests.get")
    @override_settings(SERVER_URL="http://web:8000")
    def test_pre_warm_department_page_api_successfully(self, mock_request_get):
        DepartmentFactory()

        mock_request_get.return_value.status_code = 200
        mock_request_get.return_value.json.return_value = "mock response"

        api_pre_warmer = APIPreWarmer()
        pre_warming_errors = api_pre_warmer.pre_warm_department_api()

        assert len(pre_warming_errors) == 0

    @patch("tasks.services.api_pre_warmer.requests.get")
    @override_settings(SERVER_URL="http://web:8000")
    def test_pre_warm_department_api_fail(self, mock_request_get):
        DepartmentFactory()

        mock_request_get.side_effect = Exception()

        api_pre_warmer = APIPreWarmer()
        pre_warming_errors = api_pre_warmer.pre_warm_department_api()

        assert len(pre_warming_errors) > 0
