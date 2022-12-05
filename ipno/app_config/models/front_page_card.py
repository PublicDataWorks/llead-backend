from django.db import models

from adminsortable.models import SortableMixin
from martor.models import MartorField


class FrontPageCard(SortableMixin):
    class Meta:
        ordering = ["order"]

    order = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    content = MartorField()

    def __str__(self):
        return self.content
