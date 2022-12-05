from django.db import models

from news_articles.constants import CRAWL_STATUSES
from utils.models import TimeStampsModel


class CrawlerLog(TimeStampsModel):
    status = models.CharField(max_length=32, choices=CRAWL_STATUSES)
    created_rows = models.IntegerField(null=True)
    error_rows = models.IntegerField(null=True)

    source = models.ForeignKey(
        "news_articles.NewsArticleSource",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return (
            f"{self.source.source_name.title()} log id {self.pk} on date"
            f" {str(self.created_at.date())}"
        )
