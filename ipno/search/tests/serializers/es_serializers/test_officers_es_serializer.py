from django.test import TestCase

from mock import Mock

from search.serializers.es_serializers import OfficersESSerializer
from officers.factories import OfficerFactory, EventFactory
from departments.factories import DepartmentFactory
from officers.constants import OFFICER_HIRE


class OfficersESSerializerTestCase(TestCase):
    def test_serialize(self):
        officer_1 = OfficerFactory(first_name='Kenneth', last_name='Anderson')
        officer_2 = OfficerFactory(first_name='David', last_name='Jonesworth')
        officer_3 = OfficerFactory(first_name='Anthony', last_name='Davis')
        OfficerFactory()

        department = DepartmentFactory()
        EventFactory(
            officer=officer_1,
            department=department,
            kind=OFFICER_HIRE,
            badge_no='12435',
            year=2020,
            month=5,
            day=4,
        )
        EventFactory(
            officer=officer_1,
            badge_no=None,
            year=2015,
            month=7,
            day=20,
        )

        docs = [
            Mock(id=officer_2.id),
            Mock(id=officer_1.id),
            Mock(id=officer_3.id),
        ]
        expected_result = [
            {
                'id': officer_2.id,
                'name': 'David Jonesworth',
                'badges': [],
                'department': None,
            },
            {
                'id': officer_1.id,
                'name': 'Kenneth Anderson',
                'badges': ['12435'],
                'department': {
                    'id': department.slug,
                    'name': department.name,
                },
            },
            {
                'id': officer_3.id,
                'name': 'Anthony Davis',
                'badges': [],
                'department': None,
            },
        ]

        result = OfficersESSerializer(docs).data
        assert result == expected_result
