from django.db import models

from utils.models import TimeStampsModel


class ExcludeOfficer(TimeStampsModel):
    ran_at = models.DateTimeField(null=True, blank=True)

    officers = models.ManyToManyField(
        "officers.Officer", blank=True, related_name="exclude_officers"
    )
