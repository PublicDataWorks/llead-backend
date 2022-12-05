import datetime

from django.test import TestCase

from news_articles.factories import NewsArticleFactory, NewsArticleSourceFactory
from news_articles.factories.matched_sentence_factory import MatchedSentenceFactory
from officers.factories import OfficerFactory
from search.queries import NewsArticlesSearchQuery
from utils.search_index import rebuild_search_index


class NewsArticlesSearchQueryTestCase(TestCase):
    def test_query(self):
        officer = OfficerFactory()
        source = NewsArticleSourceFactory(source_display_name="dummy")
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
            published_date=news_article_1.published_date - datetime.timedelta(days=1),
        )
        news_article_3 = NewsArticleFactory(
            title="News article 3",
            content="Text content 3",
            source=source,
            author="author keyword",
            published_date=news_article_1.published_date - datetime.timedelta(days=2),
        )
        news_article_4 = NewsArticleFactory(
            title="keyword title",
            source=source,
            published_date=news_article_1.published_date - datetime.timedelta(days=3),
            is_hidden=True,
        )
        matched_sentence_1 = MatchedSentenceFactory(article=news_article_1)
        matched_sentence_2 = MatchedSentenceFactory(article=news_article_2)
        matched_sentence_3 = MatchedSentenceFactory(article=news_article_3)
        matched_sentence_4 = MatchedSentenceFactory(article=news_article_4)
        matched_sentence_1.officers.add(officer)
        matched_sentence_2.officers.add(officer)
        matched_sentence_3.officers.add(officer)
        matched_sentence_4.officers.add(officer)

        rebuild_search_index()

        result = NewsArticlesSearchQuery("keyword").search()

        assert len(result) == 3
        assert result[0]["id"] == news_article_1.id
        assert result[1]["id"] == news_article_2.id
        assert result[2]["id"] == news_article_3.id
