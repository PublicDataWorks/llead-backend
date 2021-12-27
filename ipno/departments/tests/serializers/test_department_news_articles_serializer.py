from django.test import TestCase

from django.db.models import BooleanField
from django.db.models.expressions import Value

from departments.serializers import DepartmentNewsArticleSerializer
from news_articles.factories import NewsArticleFactory
from news_articles.models import NewsArticle


class DepartmentNewsArticleSerializerTestCase(TestCase):
    def test_data(self):
        news_article = NewsArticleFactory()

        serialized_news_article = NewsArticle.objects.filter(
            id=news_article.id
        ).annotate(
            is_starred=Value(True, output_field=BooleanField()),
        ).first()

        result = DepartmentNewsArticleSerializer(serialized_news_article).data
        assert result == {
            'id': news_article.id,
            'title': news_article.title,
            'published_date': str(news_article.published_date),
            'source_display_name': news_article.source.source_display_name,
            'is_starred': True,
            'url': news_article.url,
        }
