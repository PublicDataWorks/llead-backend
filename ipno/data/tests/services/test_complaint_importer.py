import json
from io import StringIO, BytesIO
from csv import DictWriter

from django.test.testcases import TestCase, override_settings

from mock import patch

from data.services import ComplaintImporter
from data.models import ImportLog
from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.factories import WrglRepoFactory
from complaints.models import Complaint
from complaints.factories import ComplaintFactory
from officers.factories import OfficerFactory
from departments.factories import DepartmentFactory


class ComplaintImporterTestCase(TestCase):
    def setUp(self):
        csv_content = StringIO()
        writer = DictWriter(
            csv_content,
            fieldnames=[
                'uid',
                'agency',
                'complaint_uid',
                'allegation_uid',
                'charge_uid',
                'tracking_number',
                'investigation_type',
                'investigation_status',
                'assigned_unit',
                'assigned_department',
                'assigned_division',
                'assigned_sub_division_a',
                'body_worn_camera_available',
                'app_used',
                'citizen_arrested',
                'allegation_finding',
                'allegation',
                'allegation_class',
                'citizen',
                'disposition',
                'rule_code',
                'rule_violation',
                'paragraph_code',
                'paragraph_violation',
                'charges',
                'complainant_name',
                'complainant_type',
                'complainant_sex',
                'complainant_race',
                'recommended_action',
                'action',
                'data_production_year',
                'incident_type',
                'supervisor_uid',
                'supervisor_rank',
                'badge_no',
                'department_code',
                'department_desc',
                'rank_desc',
                'employment_status',
            ]
        )
        self.complaint1_data = {
            'complaint_uid': 'complaint-uid1',
            'allegation_uid': 'allegation-uid1',
            'charge_uid': 'charge-uid1',
            'uid': 'officer-uid1',
            'tracking_number': '2018-018',
            'investigation_type': 'investigation type',
            'investigation_status': 'administrative review',
            'assigned_unit': 'unit',
            'assigned_department': 'department',
            'assigned_division': 'division',
            'assigned_sub_division_a': 'sub division a',
            'body_worn_camera_available': 'camera available',
            'app_used': 'IAPro Windows',
            'citizen_arrested': 'no',
            'allegation_finding': 'sustained',
            'allegation': 'paragraph 02 - instructions from authoritative source',
            'allegation_class': 'rule 4: perf of duty',
            'citizen': 'black female',
            'disposition': 'sustained',
            'rule_code': '1.3',
            'rule_violation': 'rule violation',
            'paragraph_code': '2',
            'paragraph_violation': '',
            'charges': '3:22 violation of known laws - 56 violations',
            'complainant_name': 'Chief Najolia ',
            'complainant_type': 'internal',
            'complainant_sex': 'female',
            'complainant_race': 'black',
            'recommended_action': 'none',
            'action': 'hold in abeyance',
            'data_production_year': '2016',
            'agency': 'New Orleans PD',
            'incident_type': 'discourtesy',
            'supervisor_uid': 'supervisor-uid1',
            'supervisor_rank': 'assistant chief',
            'badge_no': 'HP-50',
            'department_code': 'P10382',
            'department_desc': 'patrol 1st district',
            'rank_desc': 'sergeant',
            'employment_status': 'employment-status'
        }
        self.complaint2_data = {
            'complaint_uid': 'complaint-uid1',
            'allegation_uid': 'allegation-uid1',
            'charge_uid': 'charge-uid2',
            'uid': 'officer-uid1',
            'tracking_number': '',
            'investigation_type': 'administrative investigation',
            'investigation_status': '',
            'assigned_unit': '',
            'assigned_department': '',
            'assigned_division': '',
            'assigned_sub_division_a': '',
            'body_worn_camera_available': '',
            'app_used': '',
            'citizen_arrested': '',
            'allegation_finding': '',
            'allegation': '',
            'allegation_class': '',
            'citizen': '',
            'disposition': 'sustained',
            'rule_code': '',
            'rule_violation': '',
            'paragraph_code': '',
            'paragraph_violation': '',
            'charges': 'dereliction of duty - paragraph u',
            'complainant_name': '',
            'complainant_type': 'civillian ',
            'complainant_sex': 'female',
            'complainant_race': 'black',
            'recommended_action': '',
            'action': '1 day suspension without pay',
            'data_production_year': '2020',
            'agency': 'New Orleans PD',
            'incident_type': '',
            'supervisor_uid': '',
            'supervisor_rank': '',
            'badge_no': '',
            'department_code': '',
            'department_desc': '',
            'rank_desc': 'officer',
            'employment_status': ''
        }
        self.complaint3_data = {
            'complaint_uid': 'complaint-uid1',
            'allegation_uid': '',
            'charge_uid': '',
            'uid': 'officer-uid2',
            'tracking_number': '2015-2',
            'investigation_type': '',
            'investigation_status': 'complete',
            'assigned_unit': '',
            'assigned_department': '',
            'assigned_division': '',
            'assigned_sub_division_a': '',
            'body_worn_camera_available': '',
            'app_used': '',
            'citizen_arrested': '',
            'allegation_finding': '',
            'allegation': '',
            'allegation_class': '',
            'citizen': '',
            'disposition': 'not sustained',
            'rule_code': '2.0',
            'rule_violation': '',
            'paragraph_code': '3',
            'paragraph_violation': '',
            'charges': '',
            'complainant_name': '',
            'complainant_type': '',
            'complainant_sex': 'female',
            'complainant_race': 'hispanic',
            'recommended_action': 'none',
            'action': '',
            'data_production_year': '2020',
            'agency': 'Baton Rouge PD',
            'incident_type': 'discourtesy',
            'supervisor_uid': '',
            'supervisor_rank': '',
            'badge_no': 'HP-50',
            'department_code': '',
            'department_desc': 'off-duty detail',
            'rank_desc': 'police officer 2-a',
            'employment_status': ''
        }
        self.complaint4_data = {
            'complaint_uid': 'complaint-uid2',
            'allegation_uid': 'allegation-uid3',
            'charge_uid': '',
            'uid': '',
            'tracking_number': '2018-006',
            'investigation_type': '',
            'investigation_status': 'administrative review',
            'assigned_unit': '',
            'assigned_department': '',
            'assigned_division': '',
            'assigned_sub_division_a': '',
            'body_worn_camera_available': '',
            'app_used': '',
            'citizen_arrested': '',
            'allegation_finding': '',
            'allegation': '',
            'allegation_class': '',
            'citizen': '',
            'disposition': 'not sustained',
            'rule_code': '',
            'rule_violation': '',
            'paragraph_code': '',
            'paragraph_violation': '',
            'charges': '3:20 use of force - 53 hard empty hand',
            'complainant_name': '',
            'complainant_type': '',
            'complainant_sex': '',
            'complainant_race': '',
            'recommended_action': '',
            'action': 'not sustained',
            'data_production_year': '2018',
            'agency': 'New Orleans PD',
            'incident_type': '',
            'supervisor_uid': '',
            'supervisor_rank': '',
            'badge_no': '',
            'department_code': 'P10252',
            'department_desc': 'patrol 2nd district',
            'rank_desc': '',
            'employment_status': ''
        }
        self.complaint5_data = {
            'complaint_uid': 'complaint-uid3',
            'allegation_uid': '',
            'charge_uid': 'charge-uid2',
            'uid': 'officer-uid3',
            'tracking_number': '2006-0639-D',
            'investigation_type': '',
            'investigation_status': '',
            'assigned_unit': '',
            'assigned_department': '',
            'assigned_division': '',
            'assigned_sub_division_a': 'RESERVE DIVISION',
            'body_worn_camera_available': '',
            'app_used': '',
            'citizen_arrested': '',
            'allegation_finding': 'counseling',
            'allegation': 'paragraph 02 - instructions from authoritative source',
            'allegation_class': 'rule 4: perf of duty',
            'citizen': '',
            'disposition': 'counseling',
            'rule_code': '',
            'rule_violation': '',
            'paragraph_code': '',
            'paragraph_violation': '',
            'charges': 'rule 4: perf of duty; paragraph 02 - instructions from authoritative source',
            'complainant_name': '',
            'complainant_type': '',
            'complainant_sex': '',
            'complainant_race': '',
            'recommended_action': '',
            'action': '',
            'data_production_year': '2020',
            'agency': 'Baton Rouge PD',
            'incident_type': 'rank initiated',
            'supervisor_uid': '',
            'supervisor_rank': '',
            'badge_no': '',
            'department_code': '',
            'department_desc': '',
            'rank_desc': '',
            'employment_status': ''
        }
        self.complaints_data = [
            self.complaint1_data,
            self.complaint2_data,
            self.complaint3_data,
            self.complaint4_data,
            self.complaint5_data,
        ]
        writer.writeheader()
        writer.writerows(self.complaints_data)
        self.csv_stream = BytesIO(csv_content.getvalue().encode('utf-8'))

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    @patch('urllib.request.urlopen')
    def test_process_successfully(self, urlopen_mock):
        ComplaintFactory(complaint_uid='complaint-uid1', allegation_uid='allegation-uid1', charge_uid='charge-uid1')
        ComplaintFactory(complaint_uid='complaint-uid1', allegation_uid='allegation-uid1', charge_uid='charge-uid2')
        ComplaintFactory(complaint_uid='complaint-uid1', allegation_uid=None, charge_uid=None)
        ComplaintFactory(complaint_uid='complaint-uid4', allegation_uid=None, charge_uid=None)

        department_1 = DepartmentFactory(name='New Orleans PD')
        department_2 = DepartmentFactory(name='Baton Rouge PD')

        officer_1 = OfficerFactory(uid='officer-uid1')
        officer_2 = OfficerFactory(uid='officer-uid2')
        officer_3 = OfficerFactory(uid='officer-uid3')

        assert Complaint.objects.count() == 4

        WrglRepoFactory(
            data_model=ComplaintImporter.data_model,
            repo_name='complaint_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        data = {
            'hash': '3950bd17edfd805972781ef9fe2c6449'
        }
        repo_details_stream = BytesIO(json.dumps(data).encode('utf-8'))
        urlopen_mock.side_effect = [repo_details_stream, self.csv_stream]

        ComplaintImporter().process()

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == ComplaintImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 3
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Complaint.objects.count() == 5

        repo_details_request = urlopen_mock.call_args_list[0][0][0]
        assert repo_details_request._full_url == 'https://www.wrgl.co/api/v1/users/wrgl_user/repos/complaint_repo'
        assert repo_details_request.headers == {
            'Authorization': 'APIKEY wrgl-api-key'
        }

        expected_complaint1_data = self.complaint1_data.copy()
        expected_complaint1_data['department_ids'] = [department_1.id]
        expected_complaint1_data['officer_ids'] = [officer_1.id]

        expected_complaint2_data = self.complaint2_data.copy()
        expected_complaint2_data['department_ids'] = [department_1.id]
        expected_complaint2_data['officer_ids'] = [officer_1.id]

        expected_complaint3_data = self.complaint3_data.copy()
        expected_complaint3_data['department_ids'] = [department_2.id]
        expected_complaint3_data['officer_ids'] = [officer_2.id]

        expected_complaint4_data = self.complaint4_data.copy()
        expected_complaint4_data['department_ids'] = [department_1.id]
        expected_complaint4_data['officer_ids'] = []

        expected_complaint5_data = self.complaint5_data.copy()
        expected_complaint5_data['department_ids'] = [department_2.id]
        expected_complaint5_data['officer_ids'] = [officer_3.id]

        expected_complaints_data = [
            expected_complaint1_data,
            expected_complaint2_data,
            expected_complaint3_data,
            expected_complaint4_data,
            expected_complaint5_data,
        ]

        for complaint_data in expected_complaints_data:
            complaint = Complaint.objects.filter(
                complaint_uid=complaint_data['complaint_uid'] if complaint_data['complaint_uid'] else None,
                allegation_uid=complaint_data['allegation_uid'] if complaint_data['allegation_uid'] else None,
                charge_uid=complaint_data['charge_uid'] if complaint_data['charge_uid'] else None,
            ).first()
            assert complaint
            field_attrs = [
                'tracking_number',
                'investigation_type',
                'investigation_status',
                'assigned_unit',
                'assigned_department',
                'assigned_division',
                'assigned_sub_division_a',
                'body_worn_camera_available',
                'app_used',
                'citizen_arrested',
                'allegation_finding',
                'allegation',
                'allegation_class',
                'citizen',
                'disposition',
                'rule_code',
                'rule_violation',
                'paragraph_code',
                'paragraph_violation',
                'charges',
                'complainant_type',
                'complainant_sex',
                'complainant_race',
                'recommended_action',
                'action',
                'incident_type',
                'supervisor_uid',
                'supervisor_rank',
                'badge_no',
                'department_code',
                'department_desc',
                'rank_desc',
            ]
            integer_field_attrs = [
                'data_production_year',
            ]

            for attr in field_attrs:
                assert getattr(complaint, attr) == (complaint_data[attr] if complaint_data[attr] else None)

            for attr in integer_field_attrs:
                assert getattr(complaint, attr) == (int(complaint_data[attr]) if complaint_data[attr] else None)

            assert list(complaint.departments.values_list('id', flat=True)) == complaint_data['department_ids']
            assert list(complaint.officers.values_list('id', flat=True)) == complaint_data['officer_ids']
