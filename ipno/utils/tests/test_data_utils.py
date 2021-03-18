from django.test.testcases import TestCase

from utils.data_utils import data_period


class DataTestCase(TestCase):
    def test_data_period(self):
        periods = [
            [2020, 2020],
            [2012, 2015],
            [2018, 2019],
            [2014, 2016],
        ]

        years = [2009]

        assert data_period(periods, years) == ['2009', '2012-2016', '2018-2020']

        periods = [
            [2018, 2020],
            [2018, 2019],
            [2020, 2020],
        ]

        years = [2018]

        assert data_period(periods, years) == ['2018-2020']

        periods = [
            [2019, 2019],
            [2020, 2020],
        ]
        assert data_period(periods, []) == ['2019-2020']

    def test_data_period_with_empty_data(self):
        assert data_period([], []) == []
