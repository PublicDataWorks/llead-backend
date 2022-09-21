from django.db import models

from utils.models import TimeStampsModel


class AppValueConfig(TimeStampsModel):
    name = models.CharField(max_length=32)
    value = models.CharField(max_length=64)
    description = models.TextField()

    def __str__(self):
        return f'{self.name}: {self.value}'
