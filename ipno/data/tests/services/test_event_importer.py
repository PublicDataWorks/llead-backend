from decimal import Decimal
from unittest.mock import MagicMock

from django.test.testcases import TestCase, override_settings

from mock import patch, Mock

from appeals.factories import AppealFactory
from data.services import EventImporter
from data.models import ImportLog
from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.factories import WrglRepoFactory
from officers.models import Event
from officers.factories import OfficerFactory, EventFactory
from departments.factories import DepartmentFactory
from complaints.factories import ComplaintFactory
from use_of_forces.factories import UseOfForceFactory


class EventImporterTestCase(TestCase):
    def setUp(self):
        self.header = ['event_uid', 'kind', 'year', 'month', 'day', 'time', 'raw_date', 'uid', 'allegation_uid',
                       'appeal_uid', 'uof_uid', 'agency', 'badge_no', 'employee_id', 'department_code',
                       'department_desc', 'division_desc', 'sub_division_a_desc', 'sub_division_b_desc',
                       'current_supervisor', 'employee_class', 'rank_code', 'rank_desc', 'sworn',
                       'officer_inactive', 'employee_type', 'years_employed', 'salary', 'salary_freq', 'award',
                       'award_comments', 'left_reason']
        self.event1_data = ['event-uid1', 'event_pay_effective', '2017', '12', '5', '01:00', '2017-12-05',
                            'officer-uid1', 'complaint-uid1', 'appeal-uid1', '', 'New Orleans PD', '2592', '75774',
                            '5060', 'police-special operations', 'Seventh District', 'Staff', 'School Crossing Guards',
                            'current-supervisor-uid', '', '405470', 'school crossing guard', 'sworn',
                            'active', 'commissioned', '24', '27866.59', 'yearly', 'award', 'award comments',
                            'Retirement']
        self.event2_data = ['event-uid2', 'event_rank', '2008', '', '', '', '', 'officer-uid-invalid', '', '',
                            'uof-uid1', '', '', '', '', '', '', '', '', '', '', '5005', 'police event', '', '', '', '',
                            '', '', '', '', '']
        self.event3_data = ['event-uid3', 'event_pay_effective', '2009', '', '', '', '', 'officer-uid2', '', '',
                            'uof-uid2', 'Baton Rouge PD', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                            '', '67708.85', 'yearly', '', '', '']
        self.event4_data = ['event-uid4', 'event_pay_effective', '2011', '', '', '', '', '', '', '', '',
                            'New Orleans PD', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                            '86832.27', 'yearly', '', '', '']
        self.event5_data = ['event-uid5', 'event_pc_12_qualification', '2019', '11', '5', '', '2019-11-05',
                            'officer-uid3', 'complaint-uid2', '', '', 'Baton Rouge PD', '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '', '', '', '', '']

        self.event_importer = EventImporter()

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    def test_process_successfully(self):
        EventFactory(event_uid='event-uid1')
        EventFactory(event_uid='event-uid2')
        EventFactory(event_uid='event-uid3')
        EventFactory(event_uid='event-uid6')

        department_1 = DepartmentFactory(name='New Orleans PD')
        department_2 = DepartmentFactory(name='Baton Rouge PD')

        officer_1 = OfficerFactory(uid='officer-uid1')
        officer_2 = OfficerFactory(uid='officer-uid2')
        officer_3 = OfficerFactory(uid='officer-uid3')

        uof_1 = UseOfForceFactory(uof_uid='uof-uid1')
        uof_2 = UseOfForceFactory(uof_uid='uof-uid2')

        appeal_1 = AppealFactory(appeal_uid='appeal-uid1')
        appeal_2 = AppealFactory(appeal_uid='appeal-uid2')

        complaint_1 = ComplaintFactory(allegation_uid='complaint-uid1')
        complaint_3 = ComplaintFactory(allegation_uid='complaint-uid2')

        assert Event.objects.count() == 4

        WrglRepoFactory(
            data_model=EventImporter.data_model,
            repo_name='event_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        hash = '3950bd17edfd805972781ef9fe2c6449'

        self.event_importer.branch = 'main'

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        self.event_importer.repo = Mock()
        self.event_importer.new_commit = mock_commit

        self.event_importer.retrieve_wrgl_data = Mock()

        self.event_importer.old_column_mappings = {column: self.header.index(column) for column in self.header}
        self.event_importer.column_mappings = {column: self.header.index(column) for column in self.header}

        processed_data = {
            'added_rows': [
                self.event4_data,
                self.event5_data
            ],
            'deleted_rows': [
                self.event3_data,
            ],
            'updated_rows': [
                self.event1_data,
                self.event2_data,
            ],
        }

        self.event_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = self.event_importer.process()

        import_log = ImportLog.objects.order_by('-created_at').last()

        assert import_log.data_model == EventImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 2
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert result

        assert Event.objects.count() == 5

        self.event_importer.retrieve_wrgl_data.assert_called_with('event_repo')

        check_columns = self.header + ['department_id', 'officer_id', 'use_of_force_id', 'complaint_ids', 'appeal_id']
        check_column_mappings = {column: check_columns.index(column) for column in check_columns}

        expected_event1_data = self.event1_data.copy()
        expected_event1_data.append(department_1.id)
        expected_event1_data.append(officer_1.id)
        expected_event1_data.append(None)
        expected_event1_data.append({complaint_1.id})
        expected_event1_data.append({appeal_1.id})

        expected_event2_data = self.event2_data.copy()
        expected_event2_data.append(None)
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
            event = Event.objects.filter(event_uid=event_data[check_column_mappings['event_uid']]).first()
            assert event
            field_attrs = [
                'department_id',
                'officer_id',
                'use_of_force_id',
                'kind',
                'time',
                'raw_date',
                'allegation_uid',
                'appeal_uid',
                'badge_no',
                'employee_id',
                'department_code',
                'department_desc',
                'division_desc',
                'sub_division_a_desc',
                'sub_division_b_desc',
                'current_supervisor',
                'employee_class',
                'rank_code',
                'rank_desc',
                'sworn',
                'officer_inactive',
                'employee_type',
                'salary_freq',
                'award',
                'award_comments',
                'left_reason',
            ]
            integer_field_attrs = [
                'year',
                'month',
                'day',
                'years_employed',
            ]
            decimal_field_attrs = [
                'salary',
            ]

            for attr in field_attrs:
                assert getattr(event, attr) == (event_data[check_column_mappings[attr]]
                                                if event_data[check_column_mappings[attr]] else None)

            for attr in integer_field_attrs:
                assert getattr(event, attr) == (int(event_data[check_column_mappings[attr]])
                                                if event_data[check_column_mappings[attr]] else None)

            for attr in decimal_field_attrs:
                assert getattr(event, attr) == (Decimal(event_data[check_column_mappings[attr]])
                                                if event_data[check_column_mappings[attr]] else None)

            event_complaint_ids = set(event.complaints.values_list('id', flat=True))

            assert event_complaint_ids == event_data[check_column_mappings['complaint_ids']]

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    def test_process_successfully_with_columns_changed(self):
        EventFactory(event_uid='event-uid1')
        EventFactory(event_uid='event-uid2')
        EventFactory(event_uid='event-uid3')
        EventFactory(event_uid='event-uid6')

        department_1 = DepartmentFactory(name='New Orleans PD')
        department_2 = DepartmentFactory(name='Baton Rouge PD')

        officer_1 = OfficerFactory(uid='officer-uid1')
        officer_2 = OfficerFactory(uid='officer-uid2')
        officer_3 = OfficerFactory(uid='officer-uid3')

        uof_1 = UseOfForceFactory(uof_uid='uof-uid1')
        uof_2 = UseOfForceFactory(uof_uid='uof-uid2')

        appeal_1 = AppealFactory(appeal_uid='appeal-uid1')
        appeal_2 = AppealFactory(appeal_uid='appeal-uid2')

        complaint_1 = ComplaintFactory(allegation_uid='complaint-uid1')
        complaint_3 = ComplaintFactory(allegation_uid='complaint-uid2')

        assert Event.objects.count() == 4

        WrglRepoFactory(
            data_model=EventImporter.data_model,
            repo_name='event_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        hash = '3950bd17edfd805972781ef9fe2c6449'

        self.event_importer.branch = 'main'

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        self.event_importer.repo = Mock()
        self.event_importer.new_commit = mock_commit

        self.event_importer.retrieve_wrgl_data = Mock()

        old_columns = self.header[0:14] + self.header[15:]
        self.event_importer.old_column_mappings = {column: old_columns.index(column) for column in old_columns}
        self.event_importer.column_mappings = {column: self.header.index(column) for column in self.header}

        processed_data = {
            'added_rows': [
                self.event4_data,
                self.event5_data
            ],
            'deleted_rows': [
                self.event3_data[0:14] + self.event3_data[15:],
            ],
            'updated_rows': [
                self.event1_data,
                self.event2_data,
            ],
        }

        self.event_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = self.event_importer.process()

        import_log = ImportLog.objects.order_by('-created_at').last()

        assert import_log.data_model == EventImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 2
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert result

        assert Event.objects.count() == 5

        self.event_importer.retrieve_wrgl_data.assert_called_with('event_repo')

        check_columns = self.header + ['department_id', 'officer_id', 'use_of_force_id', 'complaint_ids', 'appeal_id']
        check_column_mappings = {column: check_columns.index(column) for column in check_columns}

        expected_event1_data = self.event1_data.copy()
        expected_event1_data.append(department_1.id)
        expected_event1_data.append(officer_1.id)
        expected_event1_data.append(None)
        expected_event1_data.append({complaint_1.id})
        expected_event1_data.append({appeal_1.id})

        expected_event2_data = self.event2_data.copy()
        expected_event2_data.append(None)
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
            event = Event.objects.filter(event_uid=event_data[check_column_mappings['event_uid']]).first()
            assert event
            field_attrs = [
                'department_id',
                'officer_id',
                'use_of_force_id',
                'kind',
                'time',
                'raw_date',
                'allegation_uid',
                'appeal_uid',
                'badge_no',
                'employee_id',
                'department_code',
                'department_desc',
                'division_desc',
                'sub_division_a_desc',
                'sub_division_b_desc',
                'current_supervisor',
                'employee_class',
                'rank_code',
                'rank_desc',
                'sworn',
                'officer_inactive',
                'employee_type',
                'salary_freq',
                'award',
                'award_comments',
                'left_reason',
            ]
            integer_field_attrs = [
                'year',
                'month',
                'day',
                'years_employed',
            ]
            decimal_field_attrs = [
                'salary',
            ]

            for attr in field_attrs:
                assert getattr(event, attr) == (event_data[check_column_mappings[attr]]
                                                if event_data[check_column_mappings[attr]] else None)

            for attr in integer_field_attrs:
                assert getattr(event, attr) == (int(event_data[check_column_mappings[attr]])
                                                if event_data[check_column_mappings[attr]] else None)

            for attr in decimal_field_attrs:
                assert getattr(event, attr) == (Decimal(event_data[check_column_mappings[attr]])
                                                if event_data[check_column_mappings[attr]] else None)

            event_complaint_ids = set(event.complaints.values_list('id', flat=True))

            assert event_complaint_ids == event_data[check_column_mappings['complaint_ids']]

    def test_handle_record_data_with_duplicate_uid(self):
        self.event_importer.old_column_mappings = {column: self.header.index(column) for column in self.header}
        self.event_importer.column_mappings = {column: self.header.index(column) for column in self.header}

        event = ['event-uid', 'event_pay_effective', '2017', '12', '5', '01:00', '2017-12-05', 'officer-uid1',
                 'complaint-uid1', 'appeal-uid1', '', 'New Orleans PD', '2592', '75774', '5060',
                 'police-special operations', 'Seventh District', 'Staff', 'School Crossing Guards',
                 'current-supervisor-uid', '', '405470', 'school crossing guard', 'full-time', 'sworn', 'active',
                 'commissioned', '24', '27866.59', 'yearly', 'award', 'award comments']

        self.event_importer.new_event_uids = ['event-uid']

        self.event_importer.handle_record_data(event)

        assert self.event_importer.new_event_uids == ['event-uid']

    def test_delete_row_with_non_exist_uid(self):
        EventFactory()
        self.event_importer.old_column_mappings = {column: self.header.index(column) for column in self.header}
        self.event_importer.column_mappings = {column: self.header.index(column) for column in self.header}

        event = ['event-uid', 'event_pay_effective', '2017', '12', '5', '01:00', '2017-12-05', 'officer-uid1',
                 'complaint-uid1', 'appeal-uid1', '', 'New Orleans PD', '2592', '75774', '5060',
                 'police-special operations', 'Seventh District', 'Staff', 'School Crossing Guards',
                 'current-supervisor-uid', '', '405470', 'school crossing guard', 'full-time', 'sworn', 'active',
                 'commissioned', '24', '27866.59', 'yearly', 'award', 'award comments']

        self.event_importer.new_event_uids = ['event-uid']

        self.event_importer.import_data({
            'added_rows': [],
            'updated_rows': [],
            'deleted_rows': [event],
        })

        assert self.event_importer.new_event_uids == ['event-uid']
        assert self.event_importer.delete_events_ids == []
        assert Event.objects.all().count() == 1
