from django.test import TestCase

from departments.factories import DepartmentFactory
from departments.serializers import DepartmentCoordinateSerializer


class DepartmentCoodinateSerializerTestCase(TestCase):
    def test_data(self):
        department = DepartmentFactory()

        result = DepartmentCoordinateSerializer(department).data
        assert result == {
            "id": department.slug,
            "name": department.name,
            "location": department.location,
        }
