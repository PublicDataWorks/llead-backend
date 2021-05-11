from django.db import models

from utils.models import TimeStampsModel
from martor.models import MartorField


class AppTextContent(TimeStampsModel):
    name = models.CharField(max_length=32)
    value = MartorField()
    description = models.TextField()

    def __str__(self):
        return self.name
