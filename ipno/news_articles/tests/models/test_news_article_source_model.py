from django.test.testcases import TestCase

from news_articles.factories import NewsArticleSourceFactory


class CrawlerLogTestCase(TestCase):
    def test_str(selfs):
        source = NewsArticleSourceFactory(source_name="thelens")
        assert str(source) == "thelens"
