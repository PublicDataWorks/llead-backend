from django.db import models

from utils.models import TimeStampsModel


class AnonymousItem(TimeStampsModel):
    item_id = models.CharField(max_length=255, db_index=True)
    item_type = models.CharField(max_length=255, db_index=True)
    last_visited = models.DateTimeField(auto_now=True, db_index=True)
