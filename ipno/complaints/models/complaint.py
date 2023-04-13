from django.db import models

from utils.models import APITemplateModel, TimeStampsModel


class Complaint(TimeStampsModel, APITemplateModel):
    CUSTOM_FIELDS = set()

    allegation_uid = models.CharField(
        max_length=255, null=True, blank=True, db_index=True
    )
    tracking_id = models.CharField(max_length=255, null=True, blank=True)
    uid = models.CharField(max_length=255, null=True, blank=True)
    allegation = models.TextField(null=True, blank=True)
    disposition = models.CharField(max_length=255, null=True, blank=True)
    action = models.CharField(max_length=255, null=True, blank=True)
    allegation_desc = models.TextField(null=True, blank=True)
    coaccusal = models.CharField(max_length=255, null=True, blank=True)
    agency = models.CharField(max_length=255, null=True, blank=True)

    officers = models.ManyToManyField(
        "officers.Officer", blank=True, related_name="complaints"
    )
    departments = models.ManyToManyField(
        "departments.Department", blank=True, related_name="complaints"
    )
    events = models.ManyToManyField(
        "officers.Event", blank=True, related_name="complaints"
    )

    class Meta:
        unique_together = ("allegation_uid",)

    def __str__(self):
        return f"{self.id} - {self.allegation_uid[:5]}"
