from unittest.mock import Mock
from django.test import TestCase

from departments.factories import DepartmentFactory
from departments.serializers.es_serializers import DepartmentOfficersESSerializer
from officers.constants import UOF_RECEIVE
from officers.factories import OfficerFactory, EventFactory
from people.factories import PersonFactory
from use_of_forces.factories import UseOfForceFactory


class DepartmentOfficerSerializerTestCase(TestCase):
    def test_data(self):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        person = PersonFactory(canonical_officer=officer_2, all_complaints_count=120)
        person.officers.add(officer_1)
        person.officers.add(officer_2)
        person.save()

        department = DepartmentFactory()

        use_of_force = UseOfForceFactory(officer=officer_1)

        EventFactory(
            department=department,
            officer=officer_1,
            badge_no="150",
            year=2019,
            month=2,
            day=3,
        )

        EventFactory(
            department=department,
            officer=officer_1,
            badge_no="250",
            year=2018,
            month=8,
            day=3,
        )

        EventFactory(
            department=department,
            officer=officer_2,
            badge_no="123",
            year=2018,
            month=9,
            day=3,
        )

        uof_event = EventFactory(
            department=department,
            officer=officer_1,
            kind=UOF_RECEIVE,
            year=2018,
            month=8,
            day=3,
        )

        use_of_force.events.add(uof_event)

        docs = [
            Mock(id=officer_1.id)
        ]

        result = DepartmentOfficersESSerializer(docs).data

        assert result == [
            {
                'id': officer_1.id,
                'name': officer_1.name,
                'badges': ["150", "250", "123"],
                'is_starred': False,
                'complaints_count': officer_1.person.all_complaints_count,
                'use_of_forces_count': 1,
            }
        ]
