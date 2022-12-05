from django.db import models

from utils.models import TimeStampsModel


class CrawledPost(TimeStampsModel):
    post_guid = models.CharField(max_length=255)

    source = models.ForeignKey(
        "news_articles.NewsArticleSource",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
