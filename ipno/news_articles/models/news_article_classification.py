from django.db import models

from utils.models import TimeStampsModel


class NewsArticleClassification(TimeStampsModel):
    CUSTOM_FIELDS = {"news_article"}
    BASE_FIELDS = {"id", "created_at", "updated_at"}

    article_id = models.IntegerField(unique=True, db_index=True)
    text = models.TextField()
    score = models.FloatField(default=0.0)
    relevant = models.CharField(max_length=255, blank=True, null=True)
    truth = models.CharField(max_length=255, blank=True, null=True)

    news_article = models.ForeignKey(
        "news_articles.NewsArticle",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="news_article_classifications",
    )
