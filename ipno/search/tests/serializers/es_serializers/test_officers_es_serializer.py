from django.test import TestCase

from mock import Mock

from departments.factories import DepartmentFactory
from officers.constants import OFFICER_HIRE
from officers.factories import EventFactory, OfficerFactory
from people.factories import PersonFactory
from search.serializers.es_serializers import OfficersESSerializer


class OfficersESSerializerTestCase(TestCase):
    def test_serialize(self):
        department = DepartmentFactory()

        officer_1 = OfficerFactory(
            first_name="Kenneth", last_name="Anderson", department=department
        )
        officer_2 = OfficerFactory(
            first_name="David", last_name="Jonesworth", department=department
        )
        officer_3 = OfficerFactory(
            first_name="Anthony", last_name="Davis", department=department
        )
        OfficerFactory()

        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()
        person_2 = PersonFactory(canonical_officer=officer_2)
        person_2.officers.add(officer_2)
        person_2.save()
        person_3 = PersonFactory(canonical_officer=officer_3)
        person_3.officers.add(officer_3)
        person_3.save()

        EventFactory(
            officer=officer_1,
            department=department,
            kind=OFFICER_HIRE,
            badge_no="12435",
            year=2020,
            month=5,
            day=4,
        )
        EventFactory(
            officer=officer_1,
            department=department,
            badge_no=None,
            year=2015,
            month=7,
            day=20,
        )
        EventFactory(
            department=department,
            officer=officer_1,
            rank_desc="junior",
            year=2018,
            month=4,
            day=5,
        )
        EventFactory(
            department=department,
            officer=officer_1,
            rank_desc="senior",
            year=2020,
            month=4,
            day=5,
        )
        EventFactory(
            department=department,
            officer=officer_2,
            rank_desc="senior officer",
            year=2018,
            month=4,
            day=5,
        )
        EventFactory(
            department=department,
            officer=officer_2,
            rank_desc="sergeant",
            year=2020,
            month=4,
            day=5,
        )
        EventFactory(
            department=department,
            officer=officer_3,
            rank_desc="recruit",
            year=2018,
            month=4,
            day=5,
        )
        EventFactory(
            department=department,
            officer=officer_3,
            rank_desc="lieutenant",
            year=2020,
            month=4,
            day=5,
        )

        docs = [
            Mock(id=officer_2.id),
            Mock(id=officer_1.id),
            Mock(id=officer_3.id),
        ]
        expected_result = [
            {
                "id": officer_2.id,
                "name": "David Jonesworth",
                "badges": [],
                "departments": [
                    {
                        "id": department.slug,
                        "name": department.name,
                    },
                ],
                "latest_rank": "sergeant",
            },
            {
                "id": officer_1.id,
                "name": "Kenneth Anderson",
                "badges": ["12435"],
                "departments": [
                    {
                        "id": department.slug,
                        "name": department.name,
                    },
                ],
                "latest_rank": "senior",
            },
            {
                "id": officer_3.id,
                "name": "Anthony Davis",
                "badges": [],
                "departments": [
                    {
                        "id": department.slug,
                        "name": department.name,
                    },
                ],
                "latest_rank": "lieutenant",
            },
        ]

        result = OfficersESSerializer(docs).data
        assert result == expected_result
