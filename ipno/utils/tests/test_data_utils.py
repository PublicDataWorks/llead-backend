from django.test.testcases import TestCase

from mock import Mock

from utils.data_utils import data_period, sort_items


class DataTestCase(TestCase):
    def test_data_period(self):
        years = [2018, 2019, 2009, 2012, 2013, 2014]

        assert data_period(years) == ['2009', '2012-2014', '2018-2019']

    def test_data_period_with_empty_data(self):
        assert data_period([]) == []

    def test_sorted_items(self):
        item_1 = Mock(
            key_1='20',
            key_2='a',
            key_3='x',
        )
        item_2 = Mock(
            key_1=None,
            key_2='a',
            key_3='z',
        )
        item_3 = Mock(
            key_1='16',
            key_2='b',
            key_3='z',
        )
        item_4 = Mock(
            key_1='16',
            key_2=None,
            key_3='z',
        )
        item_5 = Mock(
            key_1='16',
            key_2='a',
            key_3='z',
        )
        items = [item_1, item_2, item_3, item_4, item_5]
        expected_result = [item_5, item_3, item_4, item_1, item_2]

        assert sort_items(items, ['key_1', 'key_2']) == expected_result
