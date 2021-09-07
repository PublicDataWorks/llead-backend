from django.apps import AppConfig
from django.db import connection

from tasks.constants import APP_TASKS


class TaskConfig(AppConfig):
    name = 'tasks'

    def ready(self):
        self.on_app_ready() # noqa

    def on_app_ready(self):
        if "tasks_task" in connection.introspection.table_names():
            from tasks.models import Task
            all_task_commands = Task.objects.all().values_list('command', flat=True)

            for app_task in APP_TASKS:
                task_command = app_task['command']
                if task_command not in all_task_commands:
                    Task.objects.create(**app_task)
