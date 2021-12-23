from django.db import models
from django.contrib.postgres.fields import ArrayField

from utils.models import TimeStampsModel


class Department(TimeStampsModel):
    slug = models.CharField(max_length=255, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255, null=True, blank=True)
    parish = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    location_map_url = models.CharField(max_length=255, null=True, blank=True)
    data_period = ArrayField(models.IntegerField(), default=list)

    officers = models.ManyToManyField('officers.Officer', through='officers.Event')

    starred_officers = models.ManyToManyField(
        'officers.Officer',
        blank=True,
        related_name='starred_departments',
    )

    def __str__(self):
        return f"{self.name} - {self.id}"
