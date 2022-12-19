from django.test import TestCase

from departments.factories import OfficerMovementFactory
from departments.serializers import OfficerMovementSerializer


class OfficerMovementSerializerTestCase(TestCase):
    def test_data(self):
        officer_movement = OfficerMovementFactory()
        officer_movement.is_left = True
        officer_movement.save()

        result = OfficerMovementSerializer(officer_movement).data

        assert result == {
            "start_node": officer_movement.start_department.slug,
            "end_node": officer_movement.end_department.slug,
            "start_location": officer_movement.start_department.location,
            "end_location": officer_movement.end_department.location,
            "year": officer_movement.date.year,
            "date": officer_movement.date.strftime("%Y-%m-%d"),
            "officer_name": officer_movement.officer.name,
            "officer_id": officer_movement.officer.id,
            "left_reason": officer_movement.left_reason,
            "is_left": officer_movement.is_left,
        }
