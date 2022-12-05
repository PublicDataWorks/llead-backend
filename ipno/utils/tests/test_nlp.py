from django.test.testcases import TestCase

from mock import MagicMock, call, patch

from officers.factories import OfficerFactory
from utils.nlp import NLP


class NLPTestCase(TestCase):
    def setUp(self):
        self.nlp = NLP()

    @patch("utils.nlp.textdistance")
    def test_find_beast_match(self, mock_textdistance):
        def similarity_mock_side_effect(name, officer_name):
            return 1 if officer_name == "name1" else 0.8

        mock_textdistance.jaro_winkler.similarity.side_effect = (
            similarity_mock_side_effect
        )

        officers = {"name1": [1, 2], "name2": [3, 4]}
        result = self.nlp.find_best_match("name1", officers)

        called_similarity = [
            call("name1", "name1"),
            call("name1", "name2"),
        ]
        mock_textdistance.jaro_winkler.similarity.assert_has_calls(called_similarity)

        assert result == {"officer_ids": [1, 2], "score": 1}

    def test_process(self):
        officer1 = OfficerFactory(first_name="Jill", last_name="Sanders")
        officer2 = OfficerFactory(first_name="Kevin", last_name="Johnson")

        high_score_result = {"officer_ids": [officer1.id], "score": 1}

        low_score_result = {"officer_ids": [officer2.id], "score": 0.8}

        def find_best_match_side_effect(name, officers):
            return high_score_result if name == officer1.name else low_score_result

        find_best_match_mock = MagicMock()
        find_best_match_mock.side_effect = find_best_match_side_effect
        self.nlp.find_best_match = find_best_match_mock

        text_content = f"This is news about {officer1.name} and {officer2.name}"

        result = self.nlp.process(text_content, "officers")

        called_similarity = [
            call(officer1.name, "officers"),
            call(officer2.name, "officers"),
        ]

        self.nlp.find_best_match.assert_has_calls(called_similarity, any_order=True)

        assert result == set([officer1.id])
