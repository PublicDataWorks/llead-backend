from adminsortable.models import SortableMixin
from django.db import models


class FrontPageOrder(SortableMixin):
    class Meta:
        ordering = ['order']

    section = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    def __str__(self):
        return f'Section: {self.section}'
