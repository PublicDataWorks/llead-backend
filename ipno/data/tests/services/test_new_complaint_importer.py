from unittest.mock import MagicMock

from django.test.testcases import TestCase, override_settings

from mock import patch, Mock

from data.services import NewComplaintImporter
from data.models import ImportLog
from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.factories import WrglRepoFactory
from complaints.models import Complaint
from complaints.factories import ComplaintFactory
from officers.factories import OfficerFactory
from departments.factories import DepartmentFactory


class NewComplaintImporterTestCase(TestCase):
    def setUp(self):
        self.header = ['allegation_uid', 'uid', 'tracking_id',
                       'investigation_status', 'assigned_department', 'assigned_division',
                       'body_worn_camera_available', 'app_used', 'citizen_arrested',
                       'allegation', 'allegation_desc', 'citizen', 'disposition', 'complainant_name',
                       'complainant_type', 'complainant_sex', 'complainant_race', 'initial_action', 'action',
                       'data_production_year', 'agency', 'incident_type', 'supervisor_uid', 'supervisor_rank',
                       'badge_no', 'department_code', 'department_desc', 'rank_desc', 'employment_status',
                       'traffic_stop']

        self.complaint1_data = ['complaint-uid1-allegation-uid1-charge-uid1', 'officer-uid1', '2018-018',
                                'administrative review', 'department', 'division',
                                'camera available', 'IAPro Windows', 'no',
                                'paragraph 02 - instructions from authoritative source', 'rule 4: perf of duty',
                                'black female', 'sustained', 'Chief Najolia ', 'internal', 'female',
                                'black', 'none', 'hold in abeyance', '2016', '', 'discourtesy', 'supervisor-uid1',
                                'assistant chief', 'HP-50', 'P10382', 'patrol 1st district', 'sergeant',
                                'employment-status', 'yes']
        self.complaint2_data = ['complaint-uid1-allegation-uid1-charge-uid2', 'officer-uid-invalid', '',
                                '', '', '', '', '', '', '', '', '',
                                'sustained', '', 'civillian ',
                                'female', 'black', '', '1 day suspension without pay', '2020', '', '', '', '', '', '',
                                '', 'officer', '', 'no']
        self.complaint3_data = ['complaint-uid1', 'officer-uid2', '2015-2', 'complete', '', '', '',
                                '', '', '', '', '', 'not sustained', '', '', 'female',
                                'hispanic', 'none', '', '2020', 'baton-rouge-pd', 'discourtesy', '', '', 'HP-50', '',
                                'off-duty detail', 'police officer 2-a', '', '']
        self.complaint4_data = ['complaint-uid2-allegation-uid3', '', '2018-006', 'administrative review',
                                '', '', '', '', '', '', '', '', 'not sustained', '', '', '', '', '', 'not sustained', '2018',
                                'new-orleans-pd', '', '', '', '', 'P10252', 'patrol 2nd district', '', '', '']
        self.complaint5_data = ['complaint-uid3-charge-uid2', 'officer-uid3', '2006-0639-D', '', '', '',
                                '', '', '',
                                'paragraph 02 - instructions from authoritative source', 'rule 4: perf of duty', '',
                                'counseling', '', '',
                                '', '', '', '', '2020', 'baton-rouge-pd', 'rank initiated', '', '', '', '', '', '', '',
                                'yes']
        self.complaint6_data = ['complaint-uid6-allegation-uid6-charge-uid2', '', '',
                                '', '', '', '', '', '', '', '', '',
                                'sustained', '', 'civillian ',
                                'female', 'black', '', '1 day suspension without pay', '2020', '', '', '', '', '', '',
                                '', 'officer', '', 'no']

        self.new_complaint_importer = NewComplaintImporter()

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    def test_process_successfully(self):
        ComplaintFactory(allegation_uid='complaint-uid1-allegation-uid1-charge-uid1')
        ComplaintFactory(allegation_uid='complaint-uid1-allegation-uid1-charge-uid2')
        ComplaintFactory(allegation_uid='complaint-uid1')
        ComplaintFactory(allegation_uid='complaint-uid4')
        ComplaintFactory(allegation_uid='complaint-uid6-allegation-uid6-charge-uid2')

        department_1 = DepartmentFactory(name='New Orleans PD')
        department_2 = DepartmentFactory(name='Baton Rouge PD')

        officer_1 = OfficerFactory(uid='officer-uid1')
        OfficerFactory(uid='officer-uid2')
        officer_3 = OfficerFactory(uid='officer-uid3')

        assert Complaint.objects.count() == 5

        WrglRepoFactory(
            data_model=NewComplaintImporter.data_model,
            repo_name='complaint_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        hash = '3950bd17edfd805972781ef9fe2c6449'

        self.new_complaint_importer.branch = 'main'

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        self.new_complaint_importer.repo = Mock()
        self.new_complaint_importer.new_commit = mock_commit

        self.new_complaint_importer.retrieve_wrgl_data = Mock()

        self.new_complaint_importer.old_column_mappings = {column: self.header.index(column) for column in self.header}
        self.new_complaint_importer.column_mappings = {column: self.header.index(column) for column in self.header}

        processed_data = {
            'added_rows': [
                self.complaint1_data,
                self.complaint2_data,
                self.complaint3_data,
                self.complaint4_data,
                self.complaint5_data,
                self.complaint6_data,
            ],
            'deleted_rows': [],
            'updated_rows': [],
        }

        self.new_complaint_importer.process_wrgl_data = Mock(return_value=processed_data)

        self.new_complaint_importer.process()

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == NewComplaintImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 4
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Complaint.objects.count() == 6

        self.new_complaint_importer.retrieve_wrgl_data.assert_called_with('complaint_repo')

        self.header.extend(['department_ids', 'officer_ids'])
        self.new_complaint_importer.column_mappings = {column: self.header.index(column) for column in self.header}

        expected_complaint1_data = self.complaint1_data.copy()
        expected_complaint1_data.append([])
        expected_complaint1_data.append([officer_1.id])

        expected_complaint2_data = self.complaint2_data.copy()
        expected_complaint2_data.append([])
        expected_complaint2_data.append([])

        expected_complaint4_data = self.complaint4_data.copy()
        expected_complaint4_data.append([department_1.id])
        expected_complaint4_data.append([])

        expected_complaint5_data = self.complaint5_data.copy()
        expected_complaint5_data.append([department_2.id])
        expected_complaint5_data.append([officer_3.id])

        expected_complaint6_data = self.complaint6_data.copy()
        expected_complaint6_data.append([])
        expected_complaint6_data.append([])

        expected_complaints_data = [
            expected_complaint1_data,
            expected_complaint2_data,
            expected_complaint4_data,
            expected_complaint5_data,
        ]

        for complaint_data in expected_complaints_data:
            complaint = Complaint.objects.filter(
                allegation_uid=complaint_data[self.new_complaint_importer.column_mappings['allegation_uid']]
                if complaint_data[self.new_complaint_importer.column_mappings['allegation_uid']] else None
            ).first()
            assert complaint
            field_attrs = [
                'allegation_uid',
                'tracking_id',
                'uid',
                'allegation',
                'investigation_status',
                'assigned_department',
                'assigned_division',
                'traffic_stop',
                'body_worn_camera_available',
                'app_used',
                'citizen_arrested',
                'citizen',
                'disposition',
                'complainant_name',
                'complainant_type',
                'complainant_sex',
                'complainant_race',
                'action',
                'initial_action',
                'incident_type',
                'supervisor_uid',
                'supervisor_rank',
                'badge_no',
                'department_code',
                'department_desc',
                'employment_status',
                'allegation_desc',
            ]

            for attr in field_attrs:

                assert getattr(complaint, attr) == (complaint_data[self.new_complaint_importer.column_mappings[attr]]
                                                    if complaint_data[self.new_complaint_importer.column_mappings[attr]] else None)

            assert list(complaint.departments.values_list('id', flat=True)) == complaint_data[self.new_complaint_importer.column_mappings['department_ids']]
            assert list(complaint.officers.values_list('id', flat=True)) == complaint_data[self.new_complaint_importer.column_mappings['officer_ids']]

    def test_handle_record_data_with_duplicate_uid(self):
        self.new_complaint_importer.new_allegation_uids = ['allegation-uid']

        self.new_complaint_importer.parse_row_data = Mock()
        self.new_complaint_importer.parse_row_data.return_value = {
            'allegation_uid': 'allegation-uid',
        }

        self.new_complaint_importer.handle_record_data('row')

        assert self.new_complaint_importer.new_allegation_uids == ['allegation-uid']
