from django.test.testcases import TestCase

from utils.data_utils import data_period


class DataTestCase(TestCase):
    def test_data_period(self):
        years = [2018, 2019, 2009, 2012, 2013, 2014]

        assert data_period(years) == ['2009', '2012-2014', '2018-2019']

    def test_data_period_with_empty_data(self):
        assert data_period([]) == []
