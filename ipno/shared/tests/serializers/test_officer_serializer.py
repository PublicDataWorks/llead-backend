from django.test import TestCase

from people.factories import PersonFactory
from shared.serializers import OfficerSerializer
from officers.factories import OfficerFactory, EventFactory
from departments.factories import DepartmentFactory


class OfficerSerializerTestCase(TestCase):
    def test_data(self):
        department = DepartmentFactory()
        officer = OfficerFactory(first_name='David', last_name='Jonesworth', department=department)
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        EventFactory(
            officer=officer,
            department=department,
            badge_no='67893',
            year=2017,
            month=1,
            day=1,
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
        EventFactory(
            department=department,
            officer=officer,
            rank_desc="junior",
            year=2018,
            month=4,
            day=5,
        )
        EventFactory(
            department=department,
            officer=officer,
            rank_desc="senior",
            year=2020,
            month=4,
            day=5,
        )
        EventFactory(
            department=department,
            officer=officer,
            rank_desc="captain",
            year=2021,
            month=None,
            day=None,
        )

        result = OfficerSerializer(officer).data
        assert result == {
            'id': officer.id,
            'name': 'David Jonesworth',
            'badges': ['12435', '67893', '5432'],
            'department': {
                'id': department.slug,
                'name': department.name,
            },
            'latest_rank': 'captain',
        }
