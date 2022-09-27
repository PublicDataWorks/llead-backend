from mock import patch

from django.test.testcases import TestCase

from q_and_a.factories import SectionFactory, QuestionFactory


class QAndATestCase(TestCase):
    @patch('q_and_a.signals.delete_cache')
    def test_delete_q_and_a_list_cache_when_Section_model_is_saved(self, mock_delete_cache):
        section = SectionFactory()
        section.name = 'test'
        section.save()

        mock_delete_cache.assert_called_with('api:q-and-a-list')

    @patch('q_and_a.signals.delete_cache')
    def test_delete_q_and_a_list_cache_when_Question_model_is_saved(self, mock_delete_cache):
        question = QuestionFactory()
        question.name = 'test'
        question.save()

        mock_delete_cache.assert_called_with('api:q-and-a-list')
