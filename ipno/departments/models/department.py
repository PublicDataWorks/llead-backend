from django.db import models
from django.db.models import F

from utils.models import TimeStampsModel
from documents.models import Document
from complaints.models import Complaint


class Department(TimeStampsModel):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255, null=True, blank=True)
    parish = models.CharField(max_length=255, null=True, blank=True)
    location_map_url = models.CharField(max_length=255, null=True, blank=True)

    officers = models.ManyToManyField('officers.Officer', through='officers.OfficerHistory')

    def __str__(self):
        return f"{self.id} - {self.name}"

    def relations_for(self, klass):
        return (
            klass.objects.filter(departments__id=self.id) |
            klass.objects.filter(
                incident_date__isnull=False,
                officers__officerhistory__start_date__isnull=False,
                officers__officerhistory__end_date__isnull=False,
                incident_date__gte=F('officers__officerhistory__start_date'),
                incident_date__lte=F('officers__officerhistory__end_date'),
                officers__officerhistory__department_id=self.id,
            )
        ).distinct()

    @property
    def documents(self):
        return self.relations_for(Document)

    @property
    def complaints(self):
        return self.relations_for(Complaint)
