from django.db import models

from utils.models import TimeStampsModel


class Document(TimeStampsModel):
    title = models.CharField(max_length=255, null=True, blank=True)
