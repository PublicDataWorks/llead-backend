from django.test.testcases import TestCase

from mock import patch

from departments.factories import DepartmentFactory


class DepartmentTestCase(TestCase):
    @patch("departments.signals.cache.clear")
    def test_clear_cache_when_Department_model_is_saved(self, mock_clear_cache):
        department = DepartmentFactory()
        department.name = ""
        department.save()

        mock_clear_cache.assert_called()
