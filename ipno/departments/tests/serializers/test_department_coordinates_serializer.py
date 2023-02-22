from django.test import TestCase

from departments.factories import DepartmentFactory
from departments.serializers import DepartmentCoordinateSerializer


class DepartmentCoodinateSerializerTestCase(TestCase):
    def test_data(self):
        department = DepartmentFactory()

        result = DepartmentCoordinateSerializer(department).data
        assert result == {
            "id": department.agency_slug,
            "name": department.agency_name,
            "location": department.location,
        }
