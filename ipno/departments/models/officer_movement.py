from django.db import models

from utils.models import TimeStampsModel


class OfficerMovement(TimeStampsModel):
    start_department = models.ForeignKey(
        "departments.Department",
        on_delete=models.CASCADE,
        related_name="left_movements",
    )
    end_department = models.ForeignKey(
        "departments.Department",
        on_delete=models.CASCADE,
        related_name="hire_movements",
    )
    officer = models.ForeignKey(
        "officers.Officer", on_delete=models.CASCADE, related_name="movements"
    )
    date = models.DateField()
    left_reason = models.CharField(max_length=255, null=True, blank=True)
