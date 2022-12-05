from django.test.testcases import TestCase

from app_config.factories import AppValueConfig


class AppConfigTestCase(TestCase):
    def test_str(selfs):
        app_config = AppValueConfig(name="Name", value="Value")
        assert str(app_config) == "Name: Value"
