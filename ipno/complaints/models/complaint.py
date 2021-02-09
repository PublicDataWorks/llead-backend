from django.db import models

from utils.models import TimeStampsModel


class Complaint(TimeStampsModel):
    uid = models.CharField(max_length=255, null=True, blank=True)
    incident_date = models.DateField(null=True)

    officers = models.ManyToManyField('officers.Officer', blank=True)
