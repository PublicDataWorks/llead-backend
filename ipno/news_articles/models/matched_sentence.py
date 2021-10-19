from django.contrib.postgres.fields import ArrayField
from django.db import models

from utils.models import TimeStampsModel


class MatchedSentence(TimeStampsModel):
    text = models.TextField()

    article = models.ForeignKey('news_articles.NewsArticle', on_delete=models.CASCADE, related_name='matched_sentences')
    extracted_keywords = ArrayField(models.CharField(max_length=50), null=True, blank=True)

    officers = models.ManyToManyField('officers.Officer', blank=True, related_name='matched_sentences')
    excluded_officers = models.ManyToManyField('officers.Officer', blank=True, related_name='excluded_matched_sentences')

    def __str__(self):
        return f'{self.text[:50]}{"..." if len(self.text) > 50 else ""}'
