from django.db import models

from utils.models import TimeStampsModel


class Feedback(TimeStampsModel):
    email = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
