import datetime

from django.test import TestCase

from mock import Mock
from elasticsearch_dsl.utils import AttrDict

from news_articles.factories import NewsArticleFactory, NewsArticleSourceFactory
from officers.factories import OfficerFactory
from shared.serializers.es_serializers import NewsArticlesESSerializer


class NewsArticlesESSerializerTestCase(TestCase):
    def test_serialize(self):
        source = NewsArticleSourceFactory(custom_matching_name='Source')
        news_article_1 = NewsArticleFactory(content='Text content keywo', author='Writer Staff', source=source)
        news_article_2 = NewsArticleFactory(
            title='Dummy title',
            author='text keywo',
            source=source,
            published_date=news_article_1.published_date + datetime.timedelta(days=1)
        )
        news_article_1.officers.add(OfficerFactory())
        news_article_2.officers.add(OfficerFactory())

        docs = [
            Mock(
                id=news_article_2.id,
                meta=Mock(
                    highlight=AttrDict({'author': ['text <em>keywo</em>']}),
                ),
            ),
            Mock(
                id=news_article_1.id,
                meta=Mock(
                    highlight=AttrDict({'content': ['Text content <em>keywo</em>']}),
                ),
            ),
        ]
        expected_result = [
            {
                'id': news_article_2.id,
                'source_name': 'Source',
                'title': news_article_2.title,
                'url': news_article_2.url,
                'date': str(news_article_2.published_date),
                'author': news_article_2.author,
                'content': news_article_2.content,
                'content_highlight': None,
                'author_highlight': 'text <em>keywo</em>'
            },
            {
                'id': news_article_1.id,
                'source_name': 'Source',
                'title': news_article_1.title,
                'url': news_article_1.url,
                'date': str(news_article_1.published_date),
                'author': news_article_1.author,
                'content': news_article_1.content,
                'content_highlight': 'Text content <em>keywo</em>',
                'author_highlight': None
            },
        ]

        result = NewsArticlesESSerializer(docs).data
        assert result == expected_result
