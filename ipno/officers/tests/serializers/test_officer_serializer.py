import pytz
from datetime import datetime

from django.test import TestCase

from officers.serializers import OfficerSerializer
from officers.factories import OfficerFactory, OfficerHistoryFactory
from departments.factories import DepartmentFactory


class OfficerSerializerTestCase(TestCase):
    def test_data(self):
        officer = OfficerFactory(first_name='David', last_name='Jonesworth')
        department = DepartmentFactory()
        OfficerHistoryFactory(
            officer=officer,
            department=department,
            badge_no='12435',
            start_date=datetime(2020, 5, 4, tzinfo=pytz.utc)
        )
        OfficerHistoryFactory(
            officer=officer,
            badge_no=None,
            start_date=datetime(2015, 7, 20, tzinfo=pytz.utc)
        )

        result = OfficerSerializer(officer).data
        assert result == {
            'id': officer.id,
            'name': 'David Jonesworth',
            'badges': ['12435'],
            'department': {
                'id': department.id,
                'name': department.name,
            },
        }
