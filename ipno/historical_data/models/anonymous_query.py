from django.db import models

from utils.models import TimeStampsModel


class AnonymousQuery(TimeStampsModel):
    query = models.CharField(max_length=255, db_index=True)
    last_visited = models.DateTimeField(auto_now=True, db_index=True)
