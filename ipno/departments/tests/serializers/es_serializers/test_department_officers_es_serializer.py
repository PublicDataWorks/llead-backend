from django.test import TestCase

from mock import Mock

from departments.factories import DepartmentFactory
from departments.serializers.es_serializers import DepartmentOfficersESSerializer
from officers.constants import OFFICER_HIRE, UOF_RECEIVE
from officers.factories import EventFactory, OfficerFactory
from people.factories import PersonFactory
from use_of_forces.factories import UseOfForceFactory, UseOfForceOfficerFactory


class OfficersESSerializerTestCase(TestCase):
    def test_serialize(self):
        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()

        officer_1 = OfficerFactory(
            first_name="Kenneth", last_name="Anderson", department=department_1
        )
        person = PersonFactory(canonical_officer=officer_1, all_complaints_count=5)
        officer_1.person = person
        officer_1.save()
        officer_2 = OfficerFactory(
            first_name="Kenneth",
            last_name="Anders",
            person=person,
            department=department_2,
        )

        uof_receive_event_1 = EventFactory(
            department=department_1,
            officer=officer_1,
            kind=UOF_RECEIVE,
            year=2018,
            month=8,
            day=20,
        )
        uof_1 = UseOfForceFactory()
        UseOfForceOfficerFactory(
            officer=officer_1,
            use_of_force=uof_1,
        )
        uof_1.events.add(uof_receive_event_1)

        uof_receive_event_2 = EventFactory(
            officer=officer_1,
            department=department_1,
            kind=UOF_RECEIVE,
            year=2020,
            month=5,
            day=12,
        )
        uof_2 = UseOfForceFactory()
        UseOfForceOfficerFactory(officer=officer_1, use_of_force=uof_2)
        uof_2.events.add(uof_receive_event_2)

        EventFactory(
            officer=officer_1,
            department=department_2,
            kind=OFFICER_HIRE,
            badge_no="12345",
            year=2020,
            month=5,
            day=4,
        )
        EventFactory(
            officer=officer_2,
            department=department_2,
            badge_no="23456",
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

        docs = [Mock(id=officer_1.id)]

        expected_result = [
            {
                "id": officer_1.id,
                "name": "Kenneth Anderson",
                "is_starred": False,
                "badges": ["12345", "23456"],
                "use_of_forces_count": 2,
                "complaints_count": 5,
                "department": {
                    "id": department_1.slug,
                    "name": department_1.name,
                },
                "latest_rank": "senior",
            }
        ]

        result = DepartmentOfficersESSerializer(docs).data
        assert result == expected_result
