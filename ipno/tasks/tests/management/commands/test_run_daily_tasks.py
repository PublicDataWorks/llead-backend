from unittest.mock import call, patch

from django.test import TestCase

from tasks.constants import DAILY_TASK
from tasks.factories import TaskFactory
from tasks.management.commands.run_daily_tasks import Command
from tasks.models import TaskLog


class CommandTestCase(TestCase):
    def setUp(self):
        self.command = Command()

    @patch("tasks.management.commands.run_daily_tasks.call_command")
    def test_handle(self, mock_call_command):
        task_1 = TaskFactory(task_type=DAILY_TASK, should_run=True)
        task_2 = TaskFactory(task_type=DAILY_TASK, should_run=True)
        TaskFactory(task_type=DAILY_TASK, should_run=False)

        self.command.handle()

        expected_calls = [
            call(task_1.command),
            call(task_2.command),
        ]

        mock_call_command.assert_has_calls(expected_calls)

        task_logs = TaskLog.objects.all()

        assert task_logs.count() == 2
        assert task_logs.first().task == task_1
        assert task_logs.first().finished_at
        assert not task_logs.first().error_message

    @patch("tasks.management.commands.run_daily_tasks.logger.error")
    @patch("tasks.management.commands.run_daily_tasks.call_command")
    def test_handle_command_error(self, mock_call_command, mock_log_error):
        task = TaskFactory(task_type=DAILY_TASK, should_run=True)

        def mock_call_command_side_effect(command):
            raise Exception()

        mock_call_command.side_effect = mock_call_command_side_effect

        self.command.handle()

        mock_call_command.assert_called_with(task.command)

        task_logs = TaskLog.objects.all()

        assert task_logs.count() == 1
        assert task_logs.first().task == task
        assert task_logs.first().error_message

        mock_log_error.assert_called_with(task_logs.first().error_message)
