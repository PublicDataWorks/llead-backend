from django.test import TestCase

from shared.serializers import NewsArticleSerializer
from news_articles.factories import NewsArticleFactory, NewsArticleSourceFactory


class NewsArticleSerializerTestCase(TestCase):
    def test_data(self):
        source = NewsArticleSourceFactory(source_display_name='dummy')
        news_article = NewsArticleFactory(source=source)

        result = NewsArticleSerializer(news_article).data

        assert result == {
                'id': news_article.id,
                'date': str(news_article.published_date),
                'title': news_article.title,
                'url': news_article.url,
                'source_name': source.source_display_name,
                'author': news_article.author,
            }
