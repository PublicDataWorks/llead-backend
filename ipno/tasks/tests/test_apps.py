import sys
from unittest.mock import patch

from django.test import TestCase

from tasks.apps import TaskConfig
from tasks.constants import APP_TASKS, DAILY_TASK
from tasks.factories import TaskFactory
from tasks.models import Task


class AppsTestCase(TestCase):
    def setUp(self):
        self.task_config = TaskConfig('tasks', sys.modules[__name__])

    @patch('tasks.apps.connection.introspection.table_names')
    def test_on_app_ready(self, mock_table_names):
        mock_table_names.return_value = ['tasks_task']

        self.task_config.on_app_ready()

        tasks = Task.objects.all()

        assert tasks.count() == 2

        assert tasks.first().task_name == APP_TASKS[0].get('task_name')
        assert tasks.first().command == APP_TASKS[0].get('command')
        assert tasks.first().task_type == APP_TASKS[0].get('task_type')
        assert not tasks.first().should_run

        assert tasks.last().task_name == APP_TASKS[-1].get('task_name')
        assert tasks.last().command == APP_TASKS[-1].get('command')
        assert tasks.last().task_type == APP_TASKS[-1].get('task_type')
        assert not tasks.last().should_run

    @patch('tasks.apps.connection.introspection.table_names')
    def test_on_app_ready_with_created_commands(self, mock_table_names):
        mock_table_names.return_value = ['tasks_task']
        for app_task in APP_TASKS:
            TaskFactory(
                task_name='existed_task',
                command=app_task.get('command'),
                task_type=DAILY_TASK
            )

        self.task_config.on_app_ready()

        tasks = Task.objects.all()

        assert tasks.count() == 2

        assert tasks.first().task_name == 'existed_task'
        assert tasks.first().command == APP_TASKS[0].get('command')
        assert tasks.first().task_type == APP_TASKS[0].get('task_type')

        assert tasks.last().task_name == 'existed_task'
        assert tasks.last().command == APP_TASKS[-1].get('command')
        assert tasks.last().task_type == APP_TASKS[-1].get('task_type')

    @patch('tasks.apps.connection.introspection.table_names')
    def test_not_init_table(self, mock_table_names):
        mock_table_names.return_value = []

        self.task_config.on_app_ready()

        tasks = Task.objects.all()

        assert tasks.count() == 0
