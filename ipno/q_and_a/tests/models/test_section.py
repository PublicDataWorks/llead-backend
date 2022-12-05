from django.test.testcases import TestCase

from q_and_a.factories import SectionFactory


class SectionTestCase(TestCase):
    def test_str(selfs):
        section = SectionFactory(name="Name")
        assert str(section) == "Name"
