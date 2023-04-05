from django.test import TestCase

from departments.factories import DepartmentFactory, OfficerMovementFactory
from departments.serializers import OfficerMovementSerializer
from officers.factories import OfficerFactory


class OfficerMovementSerializerTestCase(TestCase):
    def test_data(self):
        start_department = DepartmentFactory()
        end_department = DepartmentFactory()
        officer = OfficerFactory()

        officer_movement = OfficerMovementFactory(
            start_department=start_department,
            end_department=end_department,
            officer=officer,
        )
        officer_movement.is_left = True
        officer_movement.save()

        result = OfficerMovementSerializer(officer_movement).data

        assert result == {
            "start_node": start_department.agency_slug,
            "end_node": end_department.agency_slug,
            "start_location": start_department.location,
            "end_location": end_department.location,
            "year": officer_movement.date.year,
            "date": officer_movement.date.strftime("%Y-%m-%d"),
            "officer_name": officer.name,
            "officer_id": officer.id,
            "left_reason": officer_movement.left_reason,
            "is_left": officer_movement.is_left,
        }
