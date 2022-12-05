from django.db import models

from utils.models import TimeStampsModel


class TaskLog(TimeStampsModel):
    task = models.ForeignKey(
        "tasks.Task", on_delete=models.CASCADE, related_name="task_logs"
    )
    finished_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.task.task_name} run on {str(self.created_at.date())}"
