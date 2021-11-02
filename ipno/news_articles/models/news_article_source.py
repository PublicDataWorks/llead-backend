from django.db import models

from utils.models import TimeStampsModel


class NewsArticleSource(TimeStampsModel):
    source_name = models.CharField(max_length=255)
    source_display_name = models.CharField(max_length=255)

    def __str__(self):
        return self.source_name
