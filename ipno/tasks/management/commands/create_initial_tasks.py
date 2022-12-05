from django.core.management import BaseCommand

from tasks.constants import APP_TASKS
from tasks.models import Task


class Command(BaseCommand):
    def handle(self, *args, **options):
        for task in APP_TASKS:
            task_command = Task.objects.filter(command=task["command"]).first()
            if not task_command:
                Task.objects.create(**task)
