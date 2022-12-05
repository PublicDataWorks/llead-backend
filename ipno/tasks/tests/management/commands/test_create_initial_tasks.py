from django.core.management import call_command
from django.test import TestCase

from tasks.constants import APP_TASKS
from tasks.factories import TaskFactory
from tasks.models import Task


class CreateInitialTasksSourceTestCase(TestCase):
    def test_call_command(self):
        call_command("create_initial_tasks")
        tasks = Task.objects.all()

        assert tasks.count() == len(APP_TASKS)

        for task_data in APP_TASKS:
            task_object = tasks.filter(command=task_data["command"]).first()
            assert task_object
            assert task_object.task_name == task_data["task_name"]
            assert task_object.command == task_data["command"]
            assert task_object.task_type == task_data["task_type"]

    def test_call_command_with_partial_created_data(self):
        create_task = APP_TASKS[0]
        TaskFactory(
            task_name=create_task["task_name"],
            command=create_task["command"],
            task_type=create_task["task_type"],
        )
        assert Task.objects.all().count() == 1

        call_command("create_initial_tasks")
        tasks = Task.objects.all()

        assert tasks.count() == len(APP_TASKS)

        for task_data in APP_TASKS:
            task_object = tasks.filter(command=task_data["command"]).first()
            assert task_object
            assert task_object.task_name == task_data["task_name"]
            assert task_object.command == task_data["command"]
            assert task_object.task_type == task_data["task_type"]
