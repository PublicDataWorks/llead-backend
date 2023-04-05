from django.test.testcases import TestCase

from data.services import MigrateOfficerMovement
from departments.factories import DepartmentFactory, OfficerMovementFactory
from departments.models import OfficerMovement
from officers.constants import OFFICER_HIRE, OFFICER_LEFT, UOF_OCCUR
from officers.factories import EventFactory, OfficerFactory
from people.factories import PersonFactory
from utils.parse_utils import parse_date


class MigrateOfficerMovementTestCase(TestCase):
    def test_process_successfully(self):
        old_start_department = DepartmentFactory()
        old_end_department = DepartmentFactory()
        old_officer = OfficerFactory()

        OfficerMovementFactory(
            start_department=old_start_department,
            end_department=old_end_department,
            officer=old_officer,
        )

        start_department = DepartmentFactory()
        end_department_1 = DepartmentFactory()
        end_department_2 = DepartmentFactory(location=None)

        officer_1 = OfficerFactory()
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()

        EventFactory(
            department=start_department,
            officer=officer_1,
            kind=OFFICER_LEFT,
            year=2019,
            month=4,
            day=5,
            left_reason="Resignation",
        )
        event = EventFactory(
            department=end_department_1,
            officer=officer_1,
            kind=OFFICER_HIRE,
            year=2019,
            month=6,
            day=5,
        )
        EventFactory(
            department=end_department_2,
            officer=officer_1,
            kind=OFFICER_HIRE,
            year=2019,
            month=6,
            day=5,
        )
        EventFactory(
            department=end_department_1,
            officer=officer_1,
            kind=OFFICER_HIRE,
            year=2019,
            month=6,
            day=5,
        )

        EventFactory(
            department=start_department,
            officer=officer_1,
            kind=UOF_OCCUR,
            year=2019,
            month=5,
            day=8,
        )

        assert OfficerMovement.objects.count() == 1

        MigrateOfficerMovement().process()

        assert OfficerMovement.objects.count() == 1

        officer_movement = OfficerMovement.objects.all().first()

        assert officer_movement.start_department == start_department
        assert officer_movement.end_department == end_department_1
        assert officer_movement.officer == officer_1
        assert officer_movement.date == parse_date(event.year, event.month, event.day)
        assert officer_movement.left_reason == "Resignation"

    def test_migrate_with_no_movements(self):
        start_department = DepartmentFactory()

        officer_1 = OfficerFactory()
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()

        EventFactory(
            department=start_department,
            officer=officer_1,
            kind=OFFICER_LEFT,
            year=2019,
            month=4,
            day=5,
            left_reason="Resignation",
        )

        EventFactory(
            department=start_department,
            officer=officer_1,
            kind=OFFICER_HIRE,
            year=2019,
            month=6,
            day=5,
        )

        EventFactory(
            department=start_department,
            officer=officer_1,
            kind=UOF_OCCUR,
            year=2019,
            month=5,
            day=8,
        )

        MigrateOfficerMovement().process()

        assert OfficerMovement.objects.count() == 0
