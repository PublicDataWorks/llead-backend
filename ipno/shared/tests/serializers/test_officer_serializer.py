from django.test import TestCase

from shared.serializers import OfficerSerializer
from officers.factories import OfficerFactory, EventFactory
from departments.factories import DepartmentFactory


class OfficerSerializerTestCase(TestCase):
    def test_data(self):
        officer = OfficerFactory(first_name='David', last_name='Jonesworth')
        department = DepartmentFactory()
        EventFactory(
            officer=officer,
            department=department,
            badge_no='67893',
            year=2017,
            month=None,
            day=None,
        )

        EventFactory(
            officer=officer,
            department=department,
            badge_no='12435',
            year=2020,
            month=5,
            day=4,
        )
        EventFactory(
            officer=officer,
            department=department,
            badge_no='5432',
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            badge_no=None,
            year=2015,
            month=7,
            day=20,
        )

        result = OfficerSerializer(officer).data
        result['badges'] = sorted(result['badges'])

        assert result == {
            'id': officer.id,
            'name': 'David Jonesworth',
            'badges': ['12435', '5432', '67893'],
            'department': {
                'id': department.slug,
                'name': department.name,
            },
        }
