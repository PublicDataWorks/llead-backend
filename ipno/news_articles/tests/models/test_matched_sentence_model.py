from django.test.testcases import TestCase

from news_articles.factories.matched_sentence_factory import MatchedSentenceFactory


class MatchedSentenceTestCase(TestCase):
    def test_str(selfs):
        sent = MatchedSentenceFactory(text='The lens.')
        assert str(sent) == 'The lens.'

    def test_str_long_title(selfs):
        text = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the " \
                "industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type " \
                "and scrambled it to make a type specimen book."
        sent = MatchedSentenceFactory(text=text)
        assert str(sent) == 'Lorem Ipsum is simply dummy text of the printing a...'
