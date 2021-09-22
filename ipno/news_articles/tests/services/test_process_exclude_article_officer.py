from unittest.mock import Mock

from django.test import TestCase

from news_articles.factories import NewsArticleFactory, ExcludeOfficerFactory
from news_articles.models import NewsArticle, ExcludeOfficer
from news_articles.services import ProcessExcludeArticleOfficer
from officers.factories import OfficerFactory


class ProcessExcludeArticleOfficerTestCase(TestCase):
    def setUp(self):
        self.pea = ProcessExcludeArticleOfficer()

    def test_process_inserted_officers(self):
        excluded_officer = OfficerFactory()
        article = NewsArticleFactory()
        article.officers.add(excluded_officer)

        self.pea.latest_exclude_officers = {excluded_officer}
        self.pea.last_run_exclude = set()

        self.pea.update_status = Mock()

        self.pea.process()

        self.pea.update_status.assert_called()

        test_article = NewsArticle.objects.get(id=article.id)
        assert not test_article.officers.count()
        assert test_article.excluded_officers.first() == excluded_officer

    def test_process_deleted_officers(self):
        officer = OfficerFactory()
        article = NewsArticleFactory()
        article.excluded_officers.add(officer)

        self.pea.latest_exclude_officers = set()
        self.pea.last_run_exclude = {officer}

        self.pea.update_status = Mock()

        self.pea.process()

        self.pea.update_status.assert_called()

        test_article = NewsArticle.objects.get(id=article.id)
        assert not test_article.excluded_officers.count()
        assert test_article.officers.first() == officer

    def test_update_status(self):
        exclude_officer = ExcludeOfficerFactory()
        self.pea.latest_exclude_officers_obj = exclude_officer

        self.pea.update_status()

        test_exclude_officer = ExcludeOfficer.objects.first()
        assert test_exclude_officer.ran_at

    def test_not_update_status(self):
        self.pea.latest_exclude_officers_obj = None

        self.pea.update_status()

        test_exclude_officer = ExcludeOfficer.objects.first()
        assert not test_exclude_officer
