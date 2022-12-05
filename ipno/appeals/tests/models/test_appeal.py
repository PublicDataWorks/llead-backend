from django.test.testcases import TestCase

from appeals.factories import AppealFactory


class AppealTestCase(TestCase):
    def test_str(self):
        appeal = AppealFactory()
        assert str(appeal) == f"{appeal.id} - {appeal.appeal_uid[:5]}"
