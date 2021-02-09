from django.test import TestCase

from shared.serializers import DepartmentSerializer
from departments.factories import DepartmentFactory


class DepartmentSerializerTestCase(TestCase):
    def test_data(self):
        department = DepartmentFactory()

        result = DepartmentSerializer(department).data
        assert result == {
            'id': department.id,
            'name': department.name,
            'city': department.city,
            'parish': department.parish,
            'location_map_url': department.location_map_url,
        }
