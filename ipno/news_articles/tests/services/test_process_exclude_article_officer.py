from unittest.mock import Mock

from django.test import TestCase

from news_articles.factories import ExcludeOfficerFactory
from news_articles.factories.matched_sentence_factory import MatchedSentenceFactory
from news_articles.models import ExcludeOfficer, MatchedSentence
from news_articles.services import ProcessExcludeArticleOfficer
from officers.factories import OfficerFactory


class ProcessExcludeArticleOfficerTestCase(TestCase):
    def setUp(self):
        self.pea = ProcessExcludeArticleOfficer()

    def test_process_inserted_officers(self):
        excluded_officer = OfficerFactory()
        matched_sentence = MatchedSentenceFactory()
        matched_sentence.officers.add(excluded_officer)

        self.pea.latest_exclude_officers = {excluded_officer}
        self.pea.last_run_exclude = set()

        self.pea.update_status = Mock()

        self.pea.process()

        self.pea.update_status.assert_called()

        test_matched_sentence = MatchedSentence.objects.get(id=matched_sentence.id)
        assert not test_matched_sentence.officers.count()
        assert test_matched_sentence.excluded_officers.first() == excluded_officer

    def test_process_deleted_officers(self):
        officer = OfficerFactory()
        matched_sentence = MatchedSentenceFactory()
        matched_sentence.excluded_officers.add(officer)

        self.pea.latest_exclude_officers = set()
        self.pea.last_run_exclude = {officer}

        self.pea.update_status = Mock()

        self.pea.process()

        self.pea.update_status.assert_called()

        test_matched_sentence = MatchedSentence.objects.get(id=matched_sentence.id)
        assert not test_matched_sentence.excluded_officers.count()
        assert test_matched_sentence.officers.first() == officer

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
