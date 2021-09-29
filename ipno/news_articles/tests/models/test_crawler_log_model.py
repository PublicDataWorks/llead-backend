from django.test.testcases import TestCase

from news_articles.constants import CRAWL_STATUS_FINISHED
from news_articles.factories import CrawlerLogFactory


class CrawlerLogTestCase(TestCase):
    def test_str(selfs):
        log = CrawlerLogFactory(status=CRAWL_STATUS_FINISHED)
        assert str(log) == f'{log.source.source_name.title()} log id {log.pk} on date {str(log.created_at.date())}'
