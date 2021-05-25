import json
from io import StringIO, BytesIO
from csv import DictWriter
from decimal import Decimal

from django.test.testcases import TestCase, override_settings

from mock import patch

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
        csv_content = StringIO()
        writer = DictWriter(
            csv_content,
            fieldnames=[
                'uid',
                'agency',
                'event_uid',
                'kind',
                'year',
                'month',
                'day',
                'time',
                'raw_date',
                'complaint_uid',
                'appeal_uid',
                'uof_uid',
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
                'employment_status',
                'sworn',
                'event_inactive',
                'employee_type',
                'years_employed',
                'salary',
                'salary_freq',
                'award',
                'award_comments',
            ]
        )
        self.event1_data = {
            'event_uid': 'event-uid1',
            'kind': 'event_pay_effective',
            'year': '2017',
            'month': '12',
            'day': '5',
            'time': '01:00',
            'raw_date': '2017-12-05',
            'uid': 'officer-uid1',
            'complaint_uid': 'complaint-uid1',
            'appeal_uid': 'appeal-uid1',
            'uof_uid': '',
            'agency': 'New Orleans PD',
            'badge_no': '2592',
            'employee_id': '75774',
            'department_code': '5060',
            'department_desc': 'police-special operations',
            'division_desc': 'Seventh District',
            'sub_division_a_desc': 'Staff',
            'sub_division_b_desc': 'School Crossing Guards',
            'current_supervisor': 'current-supervisor-uid',
            'employee_class': '',
            'rank_code': '405470',
            'rank_desc': 'school crossing guard',
            'employment_status': 'full-time',
            'sworn': 'sworn',
            'event_inactive': 'active',
            'employee_type': 'commissioned',
            'years_employed': '24',
            'salary': '27866.59',
            'salary_freq': 'yearly',
            'award': 'award',
            'award_comments': 'award comments'
        }
        self.event2_data = {
            'event_uid': 'event-uid2',
            'kind': 'event_rank',
            'year': '2008',
            'month': '',
            'day': '',
            'time': '',
            'raw_date': '',
            'uid': 'officer-uid-invalid',
            'complaint_uid': '',
            'appeal_uid': '',
            'uof_uid': 'uof-uid1',
            'agency': '',
            'badge_no': '',
            'employee_id': '',
            'department_code': '',
            'department_desc': '',
            'division_desc': '',
            'sub_division_a_desc': '',
            'sub_division_b_desc': '',
            'current_supervisor': '',
            'employee_class': '',
            'rank_code': '5005',
            'rank_desc': 'police event',
            'employment_status': '',
            'sworn': '',
            'event_inactive': '',
            'employee_type': '',
            'years_employed': '',
            'salary': '',
            'salary_freq': '',
            'award': '',
            'award_comments': ''
        }
        self.event3_data = {
            'event_uid': 'event-uid3',
            'kind': 'event_pay_effective',
            'year': '2009',
            'month': '',
            'day': '',
            'time': '',
            'raw_date': '',
            'uid': 'officer-uid2',
            'complaint_uid': '',
            'appeal_uid': '',
            'uof_uid': 'uof-uid2',
            'agency': 'Baton Rouge PD',
            'badge_no': '',
            'employee_id': '',
            'department_code': '',
            'department_desc': '',
            'division_desc': '',
            'sub_division_a_desc': '',
            'sub_division_b_desc': '',
            'current_supervisor': '',
            'employee_class': '',
            'rank_code': '',
            'rank_desc': '',
            'employment_status': '',
            'sworn': '',
            'event_inactive': '',
            'employee_type': '',
            'years_employed': '',
            'salary': '67708.85',
            'salary_freq': 'yearly',
            'award': '',
            'award_comments': ''
        }
        self.event4_data = {
            'event_uid': 'event-uid4',
            'kind': 'event_pay_effective',
            'year': '2011',
            'month': '',
            'day': '',
            'time': '',
            'raw_date': '',
            'uid': '',
            'complaint_uid': '',
            'appeal_uid': '',
            'uof_uid': '',
            'agency': 'New Orleans PD',
            'badge_no': '',
            'employee_id': '',
            'department_code': '',
            'department_desc': '',
            'division_desc': '',
            'sub_division_a_desc': '',
            'sub_division_b_desc': '',
            'current_supervisor': '',
            'employee_class': '',
            'rank_code': '',
            'rank_desc': '',
            'employment_status': '',
            'sworn': '',
            'event_inactive': '',
            'employee_type': '',
            'years_employed': '',
            'salary': '86832.27',
            'salary_freq': 'yearly',
            'award': '',
            'award_comments': ''
        }
        self.event5_data = {
            'event_uid': 'event-uid5',
            'kind': 'event_pc_12_qualification',
            'year': '2019',
            'month': '11',
            'day': '5',
            'time': '',
            'raw_date': '2019-11-05',
            'uid': 'officer-uid3',
            'complaint_uid': 'complaint-uid2',
            'appeal_uid': '',
            'uof_uid': '',
            'agency': 'Baton Rouge PD',
            'badge_no': '',
            'employee_id': '',
            'department_code': '',
            'department_desc': '',
            'division_desc': '',
            'sub_division_a_desc': '',
            'sub_division_b_desc': '',
            'current_supervisor': '',
            'employee_class': '',
            'rank_code': '',
            'rank_desc': '',
            'employment_status': '',
            'sworn': '',
            'event_inactive': '',
            'employee_type': '',
            'years_employed': '',
            'salary': '',
            'salary_freq': '',
            'award': '',
            'award_comments': ''
        }
        self.events_data = [
            self.event1_data,
            self.event2_data,
            self.event3_data,
            self.event4_data,
            self.event5_data,
            self.event5_data,
        ]
        writer.writeheader()
        writer.writerows(self.events_data)
        self.csv_stream = BytesIO(csv_content.getvalue().encode('utf-8'))

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    @patch('urllib.request.urlopen')
    def test_process_successfully(self, urlopen_mock):
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

        complaint_1 = ComplaintFactory(complaint_uid='complaint-uid1')
        complaint_2 = ComplaintFactory(complaint_uid='complaint-uid1')
        complaint_3 = ComplaintFactory(complaint_uid='complaint-uid2')

        assert Event.objects.count() == 4

        WrglRepoFactory(
            data_model=EventImporter.data_model,
            repo_name='event_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        data = {
            'hash': '3950bd17edfd805972781ef9fe2c6449'
        }
        repo_details_stream = BytesIO(json.dumps(data).encode('utf-8'))
        urlopen_mock.side_effect = [repo_details_stream, self.csv_stream]

        EventImporter().process()

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == EventImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 3
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Event.objects.count() == 5

        repo_details_request = urlopen_mock.call_args_list[0][0][0]
        assert repo_details_request._full_url == 'https://www.wrgl.co/api/v1/users/wrgl_user/repos/event_repo'
        assert repo_details_request.headers == {
            'Authorization': 'APIKEY wrgl-api-key'
        }

        expected_event1_data = self.event1_data.copy()
        expected_event1_data['department_id'] = department_1.id
        expected_event1_data['officer_id'] = officer_1.id
        expected_event1_data['use_of_force_id'] = None
        expected_event1_data['complaint_ids'] = {complaint_1.id, complaint_2.id}

        expected_event2_data = self.event2_data.copy()
        expected_event2_data['department_id'] = None
        expected_event2_data['officer_id'] = None
        expected_event2_data['use_of_force_id'] = uof_1.id
        expected_event2_data['complaint_ids'] = set()

        expected_event3_data = self.event3_data.copy()
        expected_event3_data['department_id'] = department_2.id
        expected_event3_data['officer_id'] = officer_2.id
        expected_event3_data['use_of_force_id'] = uof_2.id
        expected_event3_data['complaint_ids'] = set()

        expected_event4_data = self.event4_data.copy()
        expected_event4_data['department_id'] = department_1.id
        expected_event4_data['officer_id'] = None
        expected_event4_data['use_of_force_id'] = None
        expected_event4_data['complaint_ids'] = set()

        expected_event5_data = self.event5_data.copy()
        expected_event5_data['department_id'] = department_2.id
        expected_event5_data['officer_id'] = officer_3.id
        expected_event5_data['use_of_force_id'] = None
        expected_event5_data['complaint_ids'] = {complaint_3.id}

        expected_events_data = [
            expected_event1_data,
            expected_event2_data,
            expected_event3_data,
            expected_event4_data,
            expected_event5_data,
        ]

        for event_data in expected_events_data:
            event = Event.objects.filter(event_uid=event_data['event_uid']).first()
            assert event
            field_attrs = [
                'department_id',
                'officer_id',
                'use_of_force_id',
                'kind',
                'time',
                'raw_date',
                'complaint_uid',
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
                'employment_status',
                'sworn',
                'event_inactive',
                'employee_type',
                'salary_freq',
                'award',
                'award_comments',
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
                assert getattr(event, attr) == (event_data[attr] if event_data[attr] else None)

            for attr in integer_field_attrs:
                assert getattr(event, attr) == (int(event_data[attr]) if event_data[attr] else None)

            for attr in decimal_field_attrs:
                assert getattr(event, attr) == (Decimal(event_data[attr]) if event_data[attr] else None)

            assert set(event.complaints.values_list('id', flat=True)) == event_data['complaint_ids']
