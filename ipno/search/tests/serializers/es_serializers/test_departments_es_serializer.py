from django.test import TestCase

from mock import Mock

from search.serializers.es_serializers import DepartmentsESSerializer
from departments.factories import DepartmentFactory


class DepartmentsESSerializerTestCase(TestCase):
    def test_serialize(self):
        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()
        department_3 = DepartmentFactory()
        DepartmentFactory()

        docs = [
            Mock(id=department_2.id),
            Mock(id=department_1.id),
            Mock(id=department_3.id),
        ]
        expected_result = [
            {
                'id': department_2.slug,
                'name': department_2.name,
                'city': department_2.city,
                'parish': department_2.parish,
                'location_map_url': department_2.location_map_url,
            },
            {
                'id': department_1.slug,
                'name': department_1.name,
                'city': department_1.city,
                'parish': department_1.parish,
                'location_map_url': department_1.location_map_url,
            },
            {
                'id': department_3.slug,
                'name': department_3.name,
                'city': department_3.city,
                'parish': department_3.parish,
                'location_map_url': department_3.location_map_url,
            }
        ]

        result = DepartmentsESSerializer(docs).data
        assert result == expected_result
