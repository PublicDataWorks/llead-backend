from django.contrib.postgres.fields import ArrayField
from django.db import models

from utils.models import TimeStampsModel


class NewsArticle(TimeStampsModel):
    guid = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    content = models.TextField()
    published_date = models.DateField()
    author = models.CharField(max_length=255, blank=True, null=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    extracted_keywords = ArrayField(models.CharField(max_length=50), null=True, blank=True)

    source = models.ForeignKey('news_articles.NewsArticleSource', null=True, blank=True, on_delete=models.CASCADE)
    officers = models.ManyToManyField('officers.Officer', blank=True, related_name='news_articles')
    excluded_officers = models.ManyToManyField('officers.Officer', blank=True, related_name='excluded_news_articles')

    def __str__(self):
        return f'{self.title[:50]}{"..." if len(self.title) > 50 else ""}'
