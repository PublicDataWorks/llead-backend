from django.db import models

from utils.models import TimeStampsModel


class Section(TimeStampsModel):
    class Meta:
        ordering = ['order']

    order = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name
