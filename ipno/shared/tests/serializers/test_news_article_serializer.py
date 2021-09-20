from django.test import TestCase

from news_articles.models import NewsArticleSource
from shared.serializers import NewsArticleSerializer
from news_articles.factories import NewsArticleFactory


class NewsArticleSerializerTestCase(TestCase):
    def test_data(self):
        source = NewsArticleSource()
        news_article = NewsArticleFactory(source_name=source.source_name)

        result = NewsArticleSerializer(news_article).data

        assert result == {
                'id': news_article.id,
                'date': str(news_article.published_date),
                'title': news_article.title,
                'url': news_article.url,
                'source_name': source.custom_matching_name,
        }
