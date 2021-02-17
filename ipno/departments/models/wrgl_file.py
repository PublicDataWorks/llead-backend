from django.db import models

from utils.models import TimeStampsModel


class WrglFile(TimeStampsModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    slug = models.CharField(max_length=255, unique=True)
    url = models.CharField(max_length=255)
    download_url = models.CharField(max_length=255)
    position = models.IntegerField(unique=True, default=0)
    default_expanded = models.BooleanField(default=False)

    department = models.ForeignKey('departments.Department', on_delete=models.CASCADE, null=True)
