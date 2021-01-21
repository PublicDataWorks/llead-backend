from django.db import models

from utils.models import TimeStampsModel


class Department(TimeStampsModel):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255, null=True, blank=True)
    parish = models.CharField(max_length=255, null=True, blank=True)
    location_map_url = models.CharField(max_length=255, null=True, blank=True)
