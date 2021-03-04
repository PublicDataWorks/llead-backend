from django.test.testcases import TestCase

from departments.factories import DepartmentFactory


class DepartmentTestCase(TestCase):
    def test_str(self):
        department = DepartmentFactory()
        assert str(department) == f"{department.name} - {department.id}"
