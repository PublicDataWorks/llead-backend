from django.db import models

from utils.models import TimeStampsModel


class NewsArticle(TimeStampsModel):
    guid = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    link = models.TextField(unique=True)
    content = models.TextField()
    published_date = models.DateField()
    author = models.CharField(max_length=255, blank=True, null=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    is_hidden = models.BooleanField(default=False)

    is_processed = models.BooleanField(default=False)
    source = models.ForeignKey('news_articles.NewsArticleSource', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title[:50]}{"..." if len(self.title) > 50 else ""}'
