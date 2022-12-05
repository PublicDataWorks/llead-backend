from django.test.testcases import TestCase

from news_articles.factories import CrawlerErrorFactory, CrawlerLogFactory


class CrawlerErrorTestCase(TestCase):
    def test_str(selfs):
        log = CrawlerLogFactory()
        error = CrawlerErrorFactory(log=log)
        assert (
            str(error)
            == f"{error.log.source.source_name.title()} error id {error.pk} on date"
            f" {str(error.created_at.date())}"
        )
