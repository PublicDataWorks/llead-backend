from django.test import TestCase

from departments.factories import DepartmentFactory
from officers.factories import EventFactory, OfficerFactory
from people.factories import PersonFactory
from shared.serializers import OfficerSerializer


class OfficerSerializerTestCase(TestCase):
    def test_data(self):
        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()
        officer_1 = OfficerFactory(
            first_name="David", last_name="Jonesworth", department=department_1
        )
        officer_2 = OfficerFactory(
            first_name="David", last_name="Jonesworth", department=department_2
        )
        person = PersonFactory(canonical_officer=officer_2)
        person.officers.add(officer_1)
        person.officers.add(officer_2)
        person.save()

        EventFactory(
            officer=officer_1,
            department=department_1,
            badge_no="67893",
            year=2017,
            month=1,
            day=1,
        )

        EventFactory(
            officer=officer_1,
            department=department_1,
            badge_no="12435",
            year=2020,
            month=5,
            day=4,
        )
        EventFactory(
            officer=officer_1,
            department=department_1,
            badge_no="5432",
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            department=department_1,
            officer=officer_1,
            badge_no=None,
            year=2015,
            month=7,
            day=20,
        )
        EventFactory(
            department=department_2,
            officer=officer_2,
            badge_no=None,
            year=2015,
            month=7,
            day=20,
        )
        EventFactory(
            department=department_1,
            officer=officer_1,
            rank_desc="junior",
            year=2018,
            month=4,
            day=5,
        )
        EventFactory(
            department=department_1,
            officer=officer_1,
            rank_desc="senior",
            year=2020,
            month=4,
            day=5,
        )
        EventFactory(
            department=department_1,
            officer=officer_1,
            rank_desc="captain",
            year=2021,
            month=None,
            day=None,
        )

        result = OfficerSerializer(officer_1).data

        assert result == {
            "id": officer_1.id,
            "name": "David Jonesworth",
            "badges": ["12435", "67893", "5432"],
            "departments": [
                {
                    "id": department_2.slug,
                    "name": department_2.name,
                },
                {
                    "id": department_1.slug,
                    "name": department_1.name,
                },
            ],
            "latest_rank": "captain",
        }
