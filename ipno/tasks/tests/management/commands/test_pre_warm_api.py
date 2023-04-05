from django.core.management import call_command
from django.test import TestCase, override_settings

from mock import patch

from tasks.factories import TaskFactory
from tasks.models import Task, TaskLog


class PreWarmAPICommandTestCase(TestCase):
    @override_settings(SERVER_URL="http://web:8000")
    @patch("tasks.services.APIPreWarmer.pre_warm_front_page_api")
    @patch("tasks.services.APIPreWarmer.pre_warm_department_api")
    def test_call_command(
        self, pre_warm_front_page_api_mock, pre_warm_department_api_mock
    ):
        TaskFactory(command="pre_warm_api")

        pre_warm_front_page_api_mock.return_value = []
        pre_warm_department_api_mock.return_value = []

        call_command("pre_warm_api")

        pre_warm_front_page_api_mock.assert_called()
        pre_warm_department_api_mock.assert_called()

        task = Task.objects.get(command="pre_warm_api")

        task_logs = TaskLog.objects.all()

        assert task_logs.count() == 1
        assert task_logs.first().task == task
        assert not task_logs.first().error_message

    @override_settings(SERVER_URL="http://web:8000")
    @patch("tasks.services.APIPreWarmer.pre_warm_front_page_api")
    @patch("tasks.services.APIPreWarmer.pre_warm_department_api")
    def test_handle_command_error(
        self, pre_warm_front_page_api_mock, pre_warm_department_api_mock
    ):
        TaskFactory(command="pre_warm_api")

        pre_warm_front_page_api_mock.return_value = ["Test front page api error"]
        pre_warm_department_api_mock.return_value = ["Test department page api error"]

        call_command("pre_warm_api")

        pre_warm_front_page_api_mock.assert_called()
        pre_warm_department_api_mock.assert_called()

        task = Task.objects.get(command="pre_warm_api")

        task_logs = TaskLog.objects.all()

        assert task_logs.count() == 1
        assert task_logs.first().task == task
        assert (
            task_logs.first().error_message
            == "Test department page api error\nTest front page api error"
        )
