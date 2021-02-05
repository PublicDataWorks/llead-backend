import pytz
from datetime import datetime

from django.test import TestCase

from mock import Mock

from search.serializers.es_serializers import OfficersESSerializer
from officers.factories import OfficerFactory, OfficerHistoryFactory
from departments.factories import DepartmentFactory


class OfficersESSerializerTestCase(TestCase):
    def test_serialize(self):
        officer_1 = OfficerFactory(first_name='Kenneth', last_name='Anderson')
        officer_2 = OfficerFactory(first_name='David', last_name='Jonesworth')
        officer_3 = OfficerFactory(first_name='Anthony', last_name='Davis')
        OfficerFactory()

        department = DepartmentFactory()
        OfficerHistoryFactory(
            officer=officer_1,
            department=department,
            badge_no='12435',
            start_date=datetime(2020, 5, 4, tzinfo=pytz.utc)
        )
        OfficerHistoryFactory(
            officer=officer_1,
            badge_no=None,
            start_date=datetime(2015, 7, 20, tzinfo=pytz.utc)
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
                    'id': department.id,
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

        result = OfficersESSerializer().serialize(docs)
        assert result == expected_result
