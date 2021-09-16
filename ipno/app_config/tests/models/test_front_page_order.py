from django.test.testcases import TestCase

from app_config.factories import FrontPageOrderFactory


class FrontPageOrderTestCase(TestCase):
    def test_str(selfs):
        item = FrontPageOrderFactory(section='Name', order=1)
        assert str(item) == 'Section: Name'
