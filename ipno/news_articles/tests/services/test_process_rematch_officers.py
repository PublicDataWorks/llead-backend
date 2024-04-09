from unittest.mock import Mock, call

from django.test import TestCase
from django.utils import timezone

from news_articles.factories.matched_sentence_factory import MatchedSentenceFactory
from news_articles.models import MatchedSentence
from news_articles.services import ProcessRematchOfficers
from officers.factories import OfficerFactory


class ProcessRematchOfficersTestCase(TestCase):
    def setUp(self):
        start_time = timezone.now()
        self.pro = ProcessRematchOfficers(start_time)

    def test_get_updated_officers(self):
        officer = OfficerFactory(is_name_changed=True)
        sent = MatchedSentenceFactory()
        sent.officers.add(officer)
        sent.save()

        result = self.pro.get_updated_officers()

        updated_sent = MatchedSentence.objects.get(id=sent.id)
        assert not (officer in updated_sent.officers.all())
        assert result[0].id == officer.id

    def test_get_officer_data(self):
        officer1a = OfficerFactory(first_name="first_name1", last_name="last_name1")
        officer1b = OfficerFactory(first_name="first_name1", last_name="last_name1")
        officer2 = OfficerFactory(first_name="first_name2", last_name="last_name2")

        officers_data = self.pro.get_officers_data(
            [
                officer1a,
                officer1b,
                officer2,
            ]
        )

        expected_result = {
            "first_name1 last_name1": [officer1a.id, officer1b.id],
            "first_name2 last_name2": [officer2.id],
        }

        assert officers_data == expected_result

    def test_process_without_officers(self):
        self.pro.officers = []

        result = self.pro.process()

        assert not result

    def test_process_with_officers(self):
        OfficerFactory(first_name="first_name1", last_name="last_name1")
        OfficerFactory(first_name="first_name1", last_name="last_name1")
        officer2 = OfficerFactory(first_name="first_name2", last_name="last_name2")
        officer3 = OfficerFactory(first_name="first_name3", last_name="last_name3")

        sent1 = MatchedSentenceFactory()
        sent2 = MatchedSentenceFactory()

        def process_side_effect(text, officers):
            if text == sent1.text:
                return [officer2.id, officer3.id]
            else:
                return []

        self.pro.nlp.process = Mock()
        self.pro.nlp.process.side_effect = process_side_effect

        self.pro.excluded_officers_ids = [officer3.id]
        self.pro.officers = self.pro.get_officers_data([officer2, officer3])

        self.pro.process()

        expected_calls = [
            call(sent1.text, self.pro.officers),
            call(sent2.text, self.pro.officers),
        ]
        self.pro.nlp.process.assert_has_calls(expected_calls)

        assert officer2 in sent1.officers.all()
        assert officer3 in sent1.excluded_officers.all()
