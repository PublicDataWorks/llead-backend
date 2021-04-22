from django.db import models

from utils.models import TimeStampsModel


class Department(TimeStampsModel):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255, null=True, blank=True)
    parish = models.CharField(max_length=255, null=True, blank=True)
    location_map_url = models.CharField(max_length=255, null=True, blank=True)

    officers = models.ManyToManyField('officers.Officer', through='officers.Event')

    def __str__(self):
        return f"{self.name} - {self.id}"

    @property
    def document_years(self):
        return list(self.document_set.filter(
            incident_date__isnull=False,
        ).values_list('incident_date__year', flat=True))
