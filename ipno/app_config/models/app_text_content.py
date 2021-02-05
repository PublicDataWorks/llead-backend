from django.db import models

from utils.models import TimeStampsModel


class AppTextContent(TimeStampsModel):
    name = models.CharField(max_length=32)
    value = models.TextField()
    description = models.TextField()

    def __str__(self):
        return self.name
