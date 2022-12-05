from django.db import models

from martor.models import MartorField

from utils.models import TimeStampsModel


class AppTextContent(TimeStampsModel):
    name = models.CharField(max_length=32)
    value = MartorField(blank=True, null=True)
    description = models.TextField()

    def __str__(self):
        return self.name
