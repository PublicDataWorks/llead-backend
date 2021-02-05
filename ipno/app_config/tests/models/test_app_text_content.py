from django.test.testcases import TestCase

from app_config.factories import AppTextContent


class AppTextContentTestCase(TestCase):
    def test_str(selfs):
        app_text_content = AppTextContent(name='App Text Content Name')
        assert str(app_text_content) == 'App Text Content Name'
