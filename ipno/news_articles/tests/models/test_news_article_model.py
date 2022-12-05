from django.db import IntegrityError
from django.test.testcases import TestCase

from news_articles.factories import NewsArticleFactory


class NewsArticleTestCase(TestCase):
    def test_str_long_title(selfs):
        title = (
            "Lorem Ipsum is simply dummy text of the printing and typesetting industry."
            " Lorem Ipsum has been the industry's standard dummy text ever since the"
            " 1500s, when an unknown printer took a galley of type and scrambled it to"
            " make a type specimen book."
        )
        new = NewsArticleFactory(title=title)
        assert str(new) == "Lorem Ipsum is simply dummy text of the printing a..."

    def test_str_short_title(selfs):
        title = "Lorem Ipsum is simply dummy text"
        new = NewsArticleFactory(title=title)
        assert str(new) == "Lorem Ipsum is simply dummy text"

    def test_duppicated_news_articles(self):
        article_1 = NewsArticleFactory()
        with self.assertRaises(IntegrityError):
            NewsArticleFactory(link=article_1.link)
