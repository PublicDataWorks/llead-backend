from django.contrib.postgres.fields import ArrayField
from django.db import models

from utils.models import TimeStampsModel


class MatchingKeyword(TimeStampsModel):
    ran_at = models.DateTimeField(null=True, blank=True)
    keywords = ArrayField(models.CharField(max_length=50), null=True, blank=True)
