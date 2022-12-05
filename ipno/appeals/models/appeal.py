from django.db import models

from utils.models import TimeStampsModel


class Appeal(TimeStampsModel):
    appeal_uid = models.CharField(max_length=255, unique=True, db_index=True)
    docket_no = models.CharField(max_length=255, null=True, blank=True)
    counsel = models.CharField(max_length=255, null=True, blank=True)
    charging_supervisor = models.CharField(max_length=255, null=True, blank=True)
    appeal_disposition = models.CharField(max_length=255, null=True, blank=True)
    action_appealed = models.CharField(max_length=255, null=True, blank=True)
    appealed = models.CharField(max_length=255, null=True, blank=True)
    motions = models.CharField(max_length=255, null=True, blank=True)

    officer = models.ForeignKey(
        "officers.Officer", on_delete=models.CASCADE, null=True, related_name="appeals"
    )
    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.CASCADE,
        null=True,
        related_name="appeals",
    )

    def __str__(self):
        return f"{self.id} - {self.appeal_uid[:5]}"
