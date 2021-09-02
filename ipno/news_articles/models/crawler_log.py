from django.db import models

from news_articles.constants import CRAWL_STATUSES
from utils.models import TimeStampsModel


class CrawlerLog(TimeStampsModel):
    source_name = models.CharField(max_length=255)
    status = models.CharField(max_length=32, choices=CRAWL_STATUSES)
    created_rows = models.IntegerField(null=True)
    error_rows = models.IntegerField(null=True)

    def __str__(self):
        return f'{self.source_name.title()} log id {self.pk} on date {str(self.created_at.date())}'
