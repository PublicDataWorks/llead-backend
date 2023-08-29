from django.db import models

from utils.models import APITemplateModel, TimeStampsModel


class PostOfficerHistory(TimeStampsModel, APITemplateModel):
    CUSTOM_FIELDS = {"officer", "department"}

    uid = models.CharField(max_length=255, unique=True, db_index=True)
    history_id = models.CharField(max_length=255)
    agency = models.CharField(max_length=255)
    left_reason = models.CharField(max_length=255, null=True, blank=True)
    hire_date = models.DateField(null=True, blank=True)

    officer = models.ForeignKey(
        "officers.Officer",
        on_delete=models.CASCADE,
        related_name="post_officer_histories",
    )
    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.CASCADE,
        related_name="post_officer_histories",
    )

    class Meta:
        verbose_name_plural = "post_officer_histories"
