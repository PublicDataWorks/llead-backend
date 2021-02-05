from django.test.testcases import TestCase

from app_config.factories import AppConfig


class AppConfigTestCase(TestCase):
    def test_str(selfs):
        app_config = AppConfig(name='Name', value='Value')
        assert str(app_config) == 'Name: Value'
