from django.db import models

from tasks.constants import TASK_TYPES
from utils.models import TimeStampsModel


class Task(TimeStampsModel):
    task_name = models.CharField(max_length=255)
    command = models.CharField(max_length=255)
    task_type = models.CharField(max_length=32, choices=TASK_TYPES)
    should_run = models.BooleanField(default=False)

    def __str__(self):
        return (
            f'{self.task_name} {"should run" if self.should_run else "should not run"}'
        )
