from django.db import models

from utils.models import APITemplateModel, TimeStampsModel


class Brady(TimeStampsModel, APITemplateModel):
    CUSTOM_FIELDS = {"officer", "source_department", "department"}

    brady_uid = models.CharField(max_length=255, unique=True, db_index=True)
    uid = models.CharField(max_length=255)
    disposition = models.CharField(max_length=255, null=True, blank=True)
    action = models.CharField(max_length=255, null=True, blank=True)
    allegation_desc = models.TextField(null=True, blank=True)
    tracking_id_og = models.CharField(max_length=255, null=True, blank=True)
    charging_agency = models.CharField(max_length=255, null=True, blank=True)
    source_agency = models.CharField(max_length=255)
    agency = models.CharField(max_length=255)

    officer = models.ForeignKey(
        "officers.Officer",
        on_delete=models.CASCADE,
        related_name="bradies",
    )
    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.CASCADE,
        related_name="bradies",
    )

    class Meta:
        verbose_name_plural = "bradies"
