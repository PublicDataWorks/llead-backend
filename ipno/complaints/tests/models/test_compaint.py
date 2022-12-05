from django.test.testcases import TestCase

from complaints.factories import ComplaintFactory


class ComplaintTestCase(TestCase):
    def test_str(self):
        complaint = ComplaintFactory()
        assert str(complaint) == f"{complaint.id} - {complaint.allegation_uid[:5]}"
