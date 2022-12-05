from django.test.testcases import TestCase

from mock import Mock

from complaints.factories import ComplaintFactory
from departments.factories import DepartmentFactory
from departments.models import Department
from officers.constants import (
    ALLEGATION_CREATE,
    COMPLAINT_INCIDENT,
    COMPLAINT_RECEIVE,
    INVESTIGATION_COMPLETE,
    SUSPENSION_END,
    SUSPENSION_START,
    UOF_ASSIGNED,
    UOF_COMPLETED,
    UOF_CREATED,
    UOF_DUE,
    UOF_INCIDENT,
    UOF_RECEIVE,
)
from officers.factories import EventFactory
from use_of_forces.factories import UseOfForceFactory
from utils.data_utils import (
    compute_department_data_period,
    format_data_period,
    sort_items,
)


class DataTestCase(TestCase):
    def test_data_period(self):
        years = [2018, 2019, 2009, 2012, 2013, 2014]

        assert format_data_period(years) == ["2009", "2012-2014", "2018-2019"]

    def test_data_period_with_empty_data(self):
        assert format_data_period([]) == []

    def test_sorted_items(self):
        item_1 = Mock(
            key_1="20",
            key_2="a",
            key_3="x",
        )
        item_2 = Mock(
            key_1=None,
            key_2="a",
            key_3="z",
        )
        item_3 = Mock(
            key_1="16",
            key_2="b",
            key_3="z",
        )
        item_4 = Mock(
            key_1="16",
            key_2=None,
            key_3="z",
        )
        item_5 = Mock(
            key_1="16",
            key_2="a",
            key_3="z",
        )
        items = [item_1, item_2, item_3, item_4, item_5]
        expected_result = [item_5, item_3, item_4, item_1, item_2]

        assert sort_items(items, ["key_1", "key_2"]) == expected_result

    def test_compute_department_data_period(self):
        department = DepartmentFactory()

        uof_1 = UseOfForceFactory(department=department)
        uof_2 = UseOfForceFactory(department=department)
        uof_3 = UseOfForceFactory(department=department)
        uof_4 = UseOfForceFactory(department=department)
        uof_5 = UseOfForceFactory(department=department)
        uof_6 = UseOfForceFactory(department=department)

        complaint_1 = ComplaintFactory()
        complaint_2 = ComplaintFactory()
        complaint_3 = ComplaintFactory()
        complaint_4 = ComplaintFactory()
        complaint_5 = ComplaintFactory()
        complaint_6 = ComplaintFactory()

        uof_receive_event = EventFactory(
            kind=UOF_RECEIVE,
            department=department,
            year=1998,
        )

        uof_incident_event = EventFactory(
            kind=UOF_INCIDENT,
            department=department,
            year=1999,
        )

        uof_assigned_event = EventFactory(
            kind=UOF_ASSIGNED,
            department=department,
            year=2010,
        )

        uof_completed_event = EventFactory(
            kind=UOF_COMPLETED,
            department=department,
            year=2011,
        )

        uof_created_event = EventFactory(
            kind=UOF_CREATED,
            department=department,
            year=2012,
        )

        uof_due_event = EventFactory(
            kind=UOF_DUE,
            department=department,
            year=1997,
        )

        complaint_incident_event = EventFactory(
            kind=COMPLAINT_INCIDENT,
            department=department,
            year=2012,
        )

        complaint_receive_event = EventFactory(
            kind=COMPLAINT_RECEIVE,
            department=department,
            year=1999,
        )

        complaint_allegation_event = EventFactory(
            kind=ALLEGATION_CREATE,
            department=department,
            year=2020,
        )

        complaint_investigation_event = EventFactory(
            kind=INVESTIGATION_COMPLETE,
            department=department,
            year=2017,
        )

        complaint_suspension_start_event = EventFactory(
            kind=SUSPENSION_START,
            department=department,
            year=2018,
        )

        complaint_suspension_end_event = EventFactory(
            kind=SUSPENSION_END,
            department=department,
            year=2019,
        )

        uof_1.events.add(uof_receive_event)
        uof_2.events.add(uof_incident_event)
        uof_3.events.add(uof_assigned_event)
        uof_4.events.add(uof_completed_event)
        uof_5.events.add(uof_created_event)
        uof_6.events.add(uof_due_event)

        complaint_1.events.add(complaint_incident_event)
        complaint_2.events.add(complaint_receive_event)
        complaint_3.events.add(complaint_allegation_event)
        complaint_4.events.add(complaint_investigation_event)
        complaint_5.events.add(complaint_suspension_start_event)
        complaint_6.events.add(complaint_suspension_end_event)

        compute_department_data_period()

        result = Department.objects.get(slug__exact=department.slug)

        assert result.data_period == [
            1997,
            1998,
            1999,
            2010,
            2011,
            2012,
            2017,
            2018,
            2019,
            2020,
        ]
