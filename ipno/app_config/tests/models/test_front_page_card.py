from django.test.testcases import TestCase

from app_config.factories import FrontPageCardFactory


class FrontPageCardTestCase(TestCase):
    def test_str(selfs):
        front_page_card = FrontPageCardFactory(content='Content Name')
        assert str(front_page_card) == 'Content Name'
