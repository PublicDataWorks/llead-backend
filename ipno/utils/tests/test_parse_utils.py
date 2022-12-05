from datetime import date

from django.test.testcases import TestCase

from utils.parse_utils import parse_date


class ParseUtilsTestCase(TestCase):
    def test_parse_date_success(self):
        year = "1990"
        month = "12"
        day = "1"
        parsed_date = parse_date(year, month, day)

        assert parsed_date == date(1990, 12, 1)

    def test_parse_date_on_failure_return_none(self):
        assert parse_date(1990, 12, None) is None
        assert parse_date(None, 12, 1) is None
        assert parse_date(1990, None, 1) is None

        assert parse_date(1990, 12, 1999) is None

        assert parse_date("abcd", "def", "gh") is None
