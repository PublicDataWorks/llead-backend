from django.test import TestCase

from departments.factories import DepartmentFactory
from shared.serializers import DepartmentSerializer


class DepartmentSerializerTestCase(TestCase):
    def test_data(self):
        department = DepartmentFactory()

        result = DepartmentSerializer(department).data
        assert result == {
            "id": department.agency_slug,
            "name": department.agency_name,
            "city": department.city,
            "parish": department.parish,
            "location_map_url": department.location_map_url,
        }
