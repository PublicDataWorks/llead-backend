from django.db.utils import IntegrityError
from django.test.testcases import TestCase

from pytest import raises

from departments.factories import DepartmentFactory, WrglFileFactory


class WrglFileTestCase(TestCase):
    def test_unique_together(self):
        department = DepartmentFactory()
        WrglFileFactory(department=department, position=1)

        with raises(
            IntegrityError,
            match=(
                rf'Key \(department_id, "position"\)=\({department.id}, 1\) already'
                r" exists\."
            ),
        ):
            WrglFileFactory(department=department, position=1)
