from django.db import models

from utils.models import TimeStampsModel


class CrawlerError(TimeStampsModel):
    response_url = models.CharField(max_length=10000)
    response_status_code = models.CharField(max_length=32)
    error_message = models.TextField(null=True)

    log = models.ForeignKey(
        "news_articles.CrawlerLog", on_delete=models.CASCADE, related_name="errors"
    )

    def __str__(self):
        return (
            f"{self.log.source.source_name.title()} error id {self.pk} on date"
            f" {str(self.created_at.date())}"
        )
