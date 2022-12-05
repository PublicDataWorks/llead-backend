from django.test.testcases import TestCase

from use_of_forces.factories import UseOfForceFactory


class UseOfForceTestCase(TestCase):
    def test_str(self):
        uof = UseOfForceFactory()
        assert str(uof) == f"{uof.id} - {uof.uof_uid[:5]}"
