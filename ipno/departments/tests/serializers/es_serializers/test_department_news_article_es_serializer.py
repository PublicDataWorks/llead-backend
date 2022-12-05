from django.test import TestCase

from elasticsearch_dsl.utils import AttrDict
from mock import Mock

from departments.factories import DepartmentFactory
from departments.serializers.es_serializers import DepartmentNewsArticlesESSerializer
from news_articles.factories import NewsArticleFactory, NewsArticleSourceFactory
from news_articles.factories.matched_sentence_factory import MatchedSentenceFactory
from officers.factories import EventFactory, OfficerFactory


class NewsArticlesESSerializerTestCase(TestCase):
    def test_serialize(self):
        officer = OfficerFactory()
        department = DepartmentFactory()
        source = NewsArticleSourceFactory(source_display_name="Source")

        NewsArticleFactory(
            title="Document title",
            content="Text content",
            source=source,
            author="dummy",
        )
        news_article_1 = NewsArticleFactory(
            title="News article keyword1", content="Text content 1", source=source
        )
        news_article_2 = NewsArticleFactory(
            title="News article 2",
            content="Text content keyword 2",
            source=source,
        )

        matched_sentence_1 = MatchedSentenceFactory(article=news_article_1)
        matched_sentence_2 = MatchedSentenceFactory(article=news_article_2)
        matched_sentence_1.officers.add(officer)
        matched_sentence_2.officers.add(officer)

        EventFactory(
            department=department,
            officer=officer,
        )

        docs = [
            Mock(
                id=news_article_2.id,
                meta=Mock(
                    highlight=AttrDict({"author": ["text <em>keywo</em>"]}),
                ),
            ),
            Mock(
                id=news_article_1.id,
                meta=Mock(
                    highlight=AttrDict({"content": ["Text content <em>keywo</em>"]}),
                ),
            ),
        ]
        expected_result = [
            {
                "id": news_article_2.id,
                "source_name": "Source",
                "title": news_article_2.title,
                "url": news_article_2.url,
                "date": str(news_article_2.published_date),
                "author": news_article_2.author,
                "content": news_article_2.content,
                "content_highlight": None,
                "author_highlight": "text <em>keywo</em>",
            },
            {
                "id": news_article_1.id,
                "source_name": "Source",
                "title": news_article_1.title,
                "url": news_article_1.url,
                "date": str(news_article_1.published_date),
                "author": news_article_1.author,
                "content": news_article_1.content,
                "content_highlight": "Text content <em>keywo</em>",
                "author_highlight": None,
            },
        ]

        result = DepartmentNewsArticlesESSerializer(docs).data
        assert result == expected_result
