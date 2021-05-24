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
from officers.factories import EventFactory


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
        self.events_data = [
            {
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
                'uof_uid': 'uof-uid1',
                'agency': 'Baton Rouge PD',
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
            },
            {
                'event_uid': 'event-uid2',
                'kind': 'event_rank',
                'year': '2008',
                'month': '',
                'day': '',
                'time': '',
                'raw_date': '',
                'uid': 'officer-uid1',
                'complaint_uid': '',
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
            },
            {
                'event_uid': 'event-uid3',
                'kind': 'event_pay_effective',
                'year': '2009',
                'month': '',
                'day': '',
                'time': '',
                'raw_date': '',
                'uid': 'officer-uid1',
                'complaint_uid': '',
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
                'salary': '67708.85',
                'salary_freq': 'yearly',
                'award': '',
                'award_comments': ''
            },
            {
                'event_uid': 'event-uid4',
                'kind': 'event_pay_effective',
                'year': '2011',
                'month': '',
                'day': '',
                'time': '',
                'raw_date': '',
                'uid': 'officer-uid1',
                'complaint_uid': '',
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
                'salary': '86832.27',
                'salary_freq': 'yearly',
                'award': '',
                'award_comments': ''
            },
            {
                'event_uid': 'event-uid5',
                'kind': 'event_pc_12_qualification',
                'year': '2019',
                'month': '11',
                'day': '5',
                'time': '',
                'raw_date': '2019-11-05',
                'uid': 'officer-uid1',
                'complaint_uid': '',
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
            },
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

        assert Event.objects.count() == 5

        repo_details_request = urlopen_mock.call_args_list[0][0][0]
        assert repo_details_request._full_url == 'https://www.wrgl.co/api/v1/users/wrgl_user/repos/event_repo'
        assert repo_details_request.headers == {
            'Authorization': 'APIKEY wrgl-api-key'
        }

        for event_data in self.events_data:
            event = Event.objects.filter(event_uid=event_data['event_uid']).first()
            assert event
            char_field_attrs = [
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

            for attr in char_field_attrs:
                assert getattr(event, attr) == (event_data[attr] if event_data[attr] else None)

            for attr in integer_field_attrs:
                assert getattr(event, attr) == (int(event_data[attr]) if event_data[attr] else None)

            for attr in decimal_field_attrs:
                assert getattr(event, attr) == (Decimal(event_data[attr]) if event_data[attr] else None)

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == EventImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 3
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at
