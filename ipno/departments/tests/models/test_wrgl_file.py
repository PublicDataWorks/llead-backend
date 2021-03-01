from django.test.testcases import TestCase
from pytest import raises
from django.db.utils import IntegrityError

from departments.factories import WrglFileFactory, DepartmentFactory


class WrglFileTestCase(TestCase):
    def test_unique_together(self):
        department = DepartmentFactory()
        WrglFileFactory(department=department, position=1)

        with raises(IntegrityError,
                    match=rf'Key \(department_id, "position"\)=\({department.id}, 1\) already exists\.'):
            WrglFileFactory(department=department, position=1)
