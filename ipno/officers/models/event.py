from django.db import models

from officers.constants import EVENT_KINDS
from utils.models import APITemplateModel, TimeStampsModel


class Event(TimeStampsModel, APITemplateModel):
    CUSTOM_FIELDS = {
        "officer",
        "department",
        "use_of_force",
        "appeal",
        "brady",
    }

    EventKind = models.TextChoices("EventKind", EVENT_KINDS)

    event_uid = models.CharField(max_length=255, unique=True, db_index=True)
    kind = models.CharField(
        max_length=255, null=True, blank=True, db_index=True, choices=EventKind.choices
    )
    year = models.IntegerField(null=True, blank=True, db_index=True)
    month = models.IntegerField(null=True, blank=True, db_index=True)
    day = models.IntegerField(null=True, blank=True, db_index=True)
    time = models.CharField(max_length=255, null=True, blank=True)
    raw_date = models.CharField(max_length=255, null=True, blank=True)
    allegation_uid = models.CharField(max_length=255, null=True, blank=True)
    appeal_uid = models.CharField(max_length=255, null=True, blank=True)
    badge_no = models.CharField(max_length=255, null=True, blank=True)
    department_code = models.CharField(max_length=255, null=True, blank=True)
    department_desc = models.CharField(max_length=255, null=True, blank=True)
    division_desc = models.CharField(max_length=255, null=True, blank=True)
    rank_code = models.CharField(max_length=255, null=True, blank=True)
    rank_desc = models.CharField(max_length=255, null=True, blank=True)
    salary = models.DecimalField(null=True, blank=True, max_digits=8, decimal_places=2)
    overtime_annual_total = models.DecimalField(
        null=True, blank=True, max_digits=8, decimal_places=2
    )
    salary_freq = models.CharField(max_length=255, null=True, blank=True)
    left_reason = models.CharField(max_length=255, null=True, blank=True)
    award = models.CharField(max_length=255, null=True, blank=True)
    uid = models.CharField(max_length=255, null=True, blank=True)
    agency = models.CharField(max_length=255, null=True, blank=True)
    uof_uid = models.CharField(max_length=255, null=True, blank=True)
    brady_uid = models.CharField(max_length=255, null=True, blank=True)

    officer = models.ForeignKey(
        "officers.Officer", on_delete=models.CASCADE, null=True, related_name="events"
    )
    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="events",
    )
    use_of_force = models.ForeignKey(
        "use_of_forces.UseOfForce",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="events",
    )
    appeal = models.ForeignKey(
        "appeals.Appeal",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="events",
    )
    brady = models.ForeignKey(
        "brady.Brady",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="events",
    )

    def __str__(self):
        return f'{self.kind or ""} - {self.id} - {self.event_uid[:5]}'
