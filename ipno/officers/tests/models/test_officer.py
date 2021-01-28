from django.test.testcases import TestCase

from officers.factories import OfficerFactory


class OfficerTestCase(TestCase):
    def test_name(selfs):
        officer = OfficerFactory(first_name='David', last_name='Jonesworth')
        assert officer.name == 'David Jonesworth'
