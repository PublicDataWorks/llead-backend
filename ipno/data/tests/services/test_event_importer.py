from decimal import Decimal

from django.test.testcases import TestCase

from appeals.factories import AppealFactory
from complaints.factories import ComplaintFactory
from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.models import ImportLog
from data.services import EventImporter
from data.util import MockDataReconciliation
from departments.factories import DepartmentFactory
from officers.factories import EventFactory, OfficerFactory
from officers.models import Event
from use_of_forces.factories import UseOfForceFactory


class EventImporterTestCase(TestCase):
    def setUp(self):
        event_1 = EventFactory(
            event_uid="event-uid1",
            agency="new-orleans-pd",
            uid="officer-uid1",
            allegation_uid="complaint-uid1",
            appeal_uid="appeal-uid1",
            uof_uid="",
        )
        event_2 = EventFactory(
            event_uid="event-uid2",
            agency="new-orleans-pd",
            uid="officer-uid-invalid",
            allegation_uid="",
            appeal_uid="",
            uof_uid="uof-uid1",
        )
        event_3 = EventFactory(
            event_uid="event-uid3",
            agency="baton-rouge-pd",
            uid="officer-uid2",
            allegation_uid="",
            appeal_uid="",
            uof_uid="uof-uid2",
        )
        event_4 = EventFactory(
            event_uid="event-uid4",
            agency="new-orleans-pd",
            uid="",
            allegation_uid="",
            appeal_uid="",
            uof_uid="",
        )
        event_5 = EventFactory(
            event_uid="event-uid5",
            agency="baton-rouge-pd",
            uid="officer-uid3",
            allegation_uid="complaint-uid2",
            appeal_uid="",
            uof_uid="",
        )

        self.header = list(
            {field.name for field in Event._meta.fields}
            - Event.BASE_FIELDS
            - Event.CUSTOM_FIELDS
        )
        self.event1_data = [getattr(event_1, field) for field in self.header]
        self.event2_data = [getattr(event_2, field) for field in self.header]
        self.event3_data = [getattr(event_3, field) for field in self.header]
        self.event4_data = [getattr(event_4, field) for field in self.header]
        self.event5_data = [getattr(event_5, field) for field in self.header]

        Event.objects.all().delete()
        self.event_importer = EventImporter("csv_file_path")

    def test_process_successfully(self):
        EventFactory(event_uid="event-uid1")
        EventFactory(event_uid="event-uid2")
        EventFactory(event_uid="event-uid3")
        EventFactory(event_uid="event-uid6")

        department_1 = DepartmentFactory(agency_name="New Orleans PD")
        department_2 = DepartmentFactory(agency_name="Baton Rouge PD")

        officer_1 = OfficerFactory(uid="officer-uid1")
        officer_2 = OfficerFactory(uid="officer-uid2")
        officer_3 = OfficerFactory(uid="officer-uid3")

        uof_1 = UseOfForceFactory(uof_uid="uof-uid1")
        uof_2 = UseOfForceFactory(uof_uid="uof-uid2")

        appeal_1 = AppealFactory(appeal_uid="appeal-uid1")
        appeal_2 = AppealFactory(appeal_uid="appeal-uid2")

        complaint_1 = ComplaintFactory(allegation_uid="complaint-uid1")
        complaint_3 = ComplaintFactory(allegation_uid="complaint-uid2")

        processed_data = {
            "added_rows": [self.event4_data, self.event5_data],
            "deleted_rows": [
                self.event3_data,
            ],
            "updated_rows": [
                self.event1_data,
                self.event2_data,
            ],
            "columns_mapping": {
                column: self.header.index(column) for column in self.header
            },
        }

        self.event_importer.data_reconciliation = MockDataReconciliation(processed_data)

        result = self.event_importer.process()

        import_log = ImportLog.objects.order_by("-created_at").last()

        assert import_log.data_model == EventImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert not import_log.commit_hash
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 2
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert result

        assert Event.objects.count() == 5

        check_columns = self.header + [
            "department_id",
            "officer_id",
            "use_of_force_id",
            "complaint_ids",
            "appeal_id",
        ]
        check_column_mappings = {
            column: check_columns.index(column) for column in check_columns
        }

        expected_event1_data = self.event1_data.copy()
        expected_event1_data.append(department_1.id)
        expected_event1_data.append(officer_1.id)
        expected_event1_data.append(None)
        expected_event1_data.append({complaint_1.id})
        expected_event1_data.append({appeal_1.id})

        expected_event2_data = self.event2_data.copy()
        expected_event2_data.append(department_1.id)
        expected_event2_data.append(None)
        expected_event2_data.append(uof_1.id)
        expected_event2_data.append(set())
        expected_event2_data.append(None)

        expected_event3_data = self.event3_data.copy()
        expected_event3_data.append(department_2.id)
        expected_event3_data.append(officer_2.id)
        expected_event3_data.append(uof_2.id)
        expected_event3_data.append(set())
        expected_event3_data.append({appeal_2.id})

        expected_event4_data = self.event4_data.copy()
        expected_event4_data.append(department_1.id)
        expected_event4_data.append(None)
        expected_event4_data.append(None)
        expected_event4_data.append(set())
        expected_event4_data.append(None)

        expected_event5_data = self.event5_data.copy()
        expected_event5_data.append(department_2.id)
        expected_event5_data.append(officer_3.id)
        expected_event5_data.append(None)
        expected_event5_data.append({complaint_3.id})
        expected_event5_data.append(None)

        expected_events_data = [
            expected_event1_data,
            expected_event2_data,
            expected_event4_data,
            expected_event5_data,
        ]

        for event_data in expected_events_data:
            event = Event.objects.filter(
                event_uid=event_data[check_column_mappings["event_uid"]]
            ).first()
            assert event
            field_attrs = [
                "agency",
                "left_reason",
                "uof_uid",
                "time",
                "appeal_uid",
                "kind",
                "rank_desc",
                "division_desc",
                "department_desc",
                "allegation_uid",
                "rank_code",
                "salary_freq",
                "department_code",
                "badge_no",
                "overtime_annual_total",
                "uid",
                "event_uid",
                "raw_date",
            ]

            integer_field_attrs = [
                "year",
                "month",
                "day",
            ]
            decimal_field_attrs = [
                "salary",
            ]

            for attr in field_attrs:
                assert getattr(event, attr) == (
                    event_data[check_column_mappings[attr]]
                    if event_data[check_column_mappings[attr]]
                    else None
                )

            for attr in integer_field_attrs:
                assert getattr(event, attr) == (
                    int(event_data[check_column_mappings[attr]])
                    if event_data[check_column_mappings[attr]]
                    else None
                )

            for attr in decimal_field_attrs:
                assert getattr(event, attr) == (
                    Decimal(event_data[check_column_mappings[attr]])
                    if event_data[check_column_mappings[attr]]
                    else None
                )

            event_complaint_ids = set(event.complaints.values_list("id", flat=True))

            assert (
                event_complaint_ids
                == event_data[check_column_mappings["complaint_ids"]]
            )

    def test_handle_record_data_with_duplicate_uid(self):
        DepartmentFactory(agency_name="New Orleans PD")
        self.event_importer.department_mappings = (
            self.event_importer.get_department_mappings()
        )
        self.event_importer.old_column_mappings = {
            column: self.header.index(column) for column in self.header
        }
        self.event_importer.column_mappings = {
            column: self.header.index(column) for column in self.header
        }

        event = EventFactory(
            event_uid="event-uid",
            agency="new-orleans-pd",
            uid="officer-uid1",
            allegation_uid="complaint-uid1",
            appeal_uid="appeal-uid1",
            uof_uid="",
        )

        event_data = [getattr(event, field) for field in self.header]

        self.event_importer.new_event_uids = ["event-uid"]

        self.event_importer.handle_record_data(event_data)

        assert self.event_importer.new_event_uids == ["event-uid"]

    def test_delete_row_with_non_exist_uid(self):
        department = DepartmentFactory(agency_name="New Orleans PD")

        EventFactory(department=department)

        event = [
            "event-uid",
            "event_pay_effective",
            "2017",
            "12",
            "5",
            "01:00",
            "2017-12-05",
            "officer-uid1",
            "complaint-uid1",
            "appeal-uid1",
            "",
            "new-orleans-pd",
            "2592",
            "75774",
            "5060",
            "police-special operations",
            "Seventh District",
            "Staff",
            "School Crossing Guards",
            "current-supervisor-uid",
            "",
            "405470",
            "school crossing guard",
            "full-time",
            "sworn",
            "active",
            "commissioned",
            "24",
            "27866.59",
            "yearly",
            "award",
            "award comments",
        ]

        self.event_importer.new_event_uids = ["event-uid"]

        self.event_importer.data_reconciliation = MockDataReconciliation(
            {
                "added_rows": [],
                "updated_rows": [],
                "deleted_rows": [event],
                "columns_mapping": {
                    column: self.header.index(column) for column in self.header
                },
            }
        )
        self.event_importer.process()

        assert self.event_importer.new_event_uids == ["event-uid"]
        assert self.event_importer.delete_events_ids == []
        assert Event.objects.all().count() == 1
