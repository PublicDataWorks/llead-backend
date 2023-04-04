from django.db import models

from utils.models import APITemplateModel, TimeStampsModel


class UseOfForce(TimeStampsModel, APITemplateModel):
    CUSTOM_FIELDS = {
        "officer",
        "department",
    }

    uof_uid = models.CharField(max_length=255, unique=True, db_index=True)
    uid = models.CharField(max_length=255, null=True, blank=True)
    tracking_id = models.CharField(max_length=255, null=True, blank=True)
    service_type = models.CharField(max_length=255, null=True, blank=True)
    disposition = models.CharField(max_length=255, null=True, blank=True)
    use_of_force_description = models.CharField(max_length=255, null=True, blank=True)
    officer_injured = models.CharField(max_length=255, null=True, blank=True)
    agency = models.CharField(max_length=255, null=True, blank=True)
    use_of_force_reason = models.CharField(max_length=255, null=True, blank=True)

    officer = models.ForeignKey(
        "officers.Officer",
        on_delete=models.CASCADE,
        null=True,
        related_name="use_of_forces",
    )
    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.CASCADE,
        null=True,
        related_name="use_of_forces",
    )

    def __str__(self):
        return f"{self.id} - {self.uof_uid[:5]}"
