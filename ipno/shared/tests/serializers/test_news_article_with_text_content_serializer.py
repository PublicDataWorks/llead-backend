from django.test import TestCase

from mock import patch

from news_articles.factories import NewsArticleFactory, NewsArticleSourceFactory
from news_articles.factories.matched_sentence_factory import MatchedSentenceFactory
from officers.factories import OfficerFactory
from shared.serializers import NewsArticleWithTextContentSerializer


class NewsArticleWithTextContentSerializerTestCase(TestCase):
    def test_data(self):
        source = NewsArticleSourceFactory(custom_matching_name='Source')
        news_article_1 = NewsArticleFactory(content='Text content keywo', author='Writer Staff', source=source)
        matched_sentence_1 = MatchedSentenceFactory(article=news_article_1)
        matched_sentence_1.officers.add(OfficerFactory())

        result = NewsArticleWithTextContentSerializer(news_article_1).data

        assert result == {
            'id': news_article_1.id,
            'source_name': 'Source',
            'title': news_article_1.title,
            'url': news_article_1.url,
            'date': str(news_article_1.published_date),
            'author': news_article_1.author,
            'content': news_article_1.content,
        }

    @patch('shared.serializers.news_article_with_text_content_serializer.TEXT_CONTENT_LIMIT', 15)
    def test_text_content(self):
        news_article = NewsArticleFactory(content='This is a very long text')

        result = NewsArticleWithTextContentSerializer(news_article).data

        assert result['content'] == 'This is a very '
