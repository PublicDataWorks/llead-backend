from django.db import models
from django.contrib.postgres.fields import ArrayField

from utils.models import TimeStampsModel


class Department(TimeStampsModel):
    slug = models.CharField(max_length=255, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255, null=True, blank=True)
    parish = models.CharField(max_length=255, null=True, blank=True)
    location_map_url = models.CharField(max_length=255, null=True, blank=True)
    data_period = ArrayField(models.IntegerField(), default=list)

    officers = models.ManyToManyField('officers.Officer', through='officers.Event')

    def __str__(self):
        return f"{self.name} - {self.id}"
