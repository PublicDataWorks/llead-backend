from django.test import TestCase

from departments.serializers import DepartmentCoordinateSerializer
from departments.factories import DepartmentFactory


class DepartmentCoodinateSerializerTestCase(TestCase):
    def test_data(self):
        department = DepartmentFactory()

        result = DepartmentCoordinateSerializer(department).data
        assert result == {
            'id': department.slug,
            'name': department.name,
            'location': department.location,
        }
