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

    source = models.ForeignKey('news_articles.NewsArticleSource', null=True, blank=True, on_delete=models.CASCADE)
    officers = models.ManyToManyField('officers.Officer', blank=True, related_name='news_articles')
