from unittest.mock import MagicMock

from django.test.testcases import TestCase, override_settings

from mock import patch, Mock

from data.services import UofImporter
from data.models import ImportLog
from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.factories import WrglRepoFactory
from use_of_forces.models import UseOfForce
from use_of_forces.factories import UseOfForceFactory
from officers.factories import OfficerFactory
from departments.factories import DepartmentFactory


class UofImporterTestCase(TestCase):
    def setUp(self):
        self.header = ['uof_uid', 'uof_tracking_number', 'report_year', 'uid', 'force_description', 'force_type',
                       'force_level', 'effective_uof', 'accidental_discharge', 'less_than_lethal', 'status', 'source',
                       'service_type', 'county', 'traffic_stop', 'sustained', 'force_reason', 'weather_description',
                       'distance_from_officer', 'body_worn_camera_available', 'app_used', 'citizen_uid',
                       'citizen_arrested', 'citizen_hospitalized', 'citizen_injured', 'citizen_body_type',
                       'citizen_height', 'citizen_age', 'citizen_involvement', 'disposition', 'citizen_sex',
                       'citizen_race', 'citizen_age_1', 'officer_current_supervisor', 'officer_title',
                       'officer_injured', 'officer_age', 'officer_years_exp', 'officer_years_with_unit', 'officer_type',
                       'officer_employment_status', 'officer_department', 'officer_division', 'officer_sub_division_a',
                       'officer_sub_division_b', 'agency']
        self.uof1_data = ['uof-uid1', 'FTN2015-0705', '2015', 'officer-uid1', 'L2-CEW Deployment', 'L2-Taser', 'L2',
                          'yes', 'no', 'yes', 'Completed', 'source', 'Pedestrian Stop', 'Orleans Parish', 'no', 'no',
                          'resisting lawful arrest', 'clear conditions', '4 feet to 6 feet', 'yes', 'blueteam',
                          'citizen-uid-1', 'yes', 'no', 'no', 'medium', "5'10'' to 6'0''", '24', 'complainant',
                          'Authorized', 'male', 'black', '25', '821', 'senior police officer', 'no', '27', '6', '3',
                          'commissioned', 'active', 'ISB - Investigations and Support Bureau',
                          'Special Investigations Division', 'Street Gang Unit', 'Squad A', 'New Orleans PD']
        self.uof2_data = ['uof-uid2', 'FTN2015-0710', '2015', 'officer-uid-invalid', 'L1-Hands', 'Hands / Escort tech',
                          'L1', 'yes', '', '', 'Completed', '', 'Call for Service', 'Orleans Parish', 'no', 'no',
                          'refuse verbal commands', 'clear conditions', '0 feet to 1 feet', 'yes', 'blueteam',
                          'citizen-uid-2', 'no', 'no', 'no', 'large', "> 6'3''", '48', 'complainant', 'Authorized',
                          'male', 'black', '48', '', 'senior police officer', 'no', '42', '14', '4', 'commissioned',
                          'active', 'FOB - Field Operations Bureau', 'Second District', 'C Platoon', '', '']
        self.uof3_data = ['uof-uid3', 'FTN2015-0713', '2015', 'officer-uid2', 'L1-Firearm (Exhibited)',
                          'Firearm Exhibited', 'L1', 'yes', '', '', 'Completed', '', 'Serving a Warrant',
                          'Orleans Parish', 'no', 'no', 'other', 'clear conditions', '1 feet to 3 feet', 'yes',
                          'blueteam', 'citizen-uid-3', 'yes', 'no', 'no', 'small', "5'7'' to 5'9''", '35',
                          'complainant', 'Authorized', 'female', 'black', '35', '3585', 'senior police officer', 'no',
                          '29', '8', '4', 'commissioned', 'active', 'FOB - Field Operations Bureau',
                          'Special Operations Division', 'Tactical Section', 'Admin Unit', 'Baton Rouge PD']
        self.uof4_data = ['uof-uid4', 'FTN2015-0735', '2015', '', 'L1-Firearm (Exhibited)', 'Firearm Exhibited', 'L1',
                          'yes', '', '', 'Completed', '', 'Serving a Warrant', 'Orleans Parish', 'no', 'no', 'other',
                          'rainy conditions - medium', '11 feet to 14 feet', 'yes', 'blueteam', 'citizen-uid-4', 'no',
                          'no', 'no', 'medium', "5'7'' to 5'9''", '14', 'complainant', 'Authorized', 'female', 'black',
                          '14', '3682', 'senior police officer', 'no', '32', '10', '2', 'commissioned', 'active',
                          'FOB - Field Operations Bureau', 'Special Operations Division', 'Tactical Section',
                          'Armory Unit', 'New Orleans PD']
        self.uof5_data = ['uof-uid5', 'FTN2016-0026', '2016', 'officer-uid3', 'L1-Firearm (Exhibited)',
                          'Firearm Exhibited', 'L1', 'yes', '', '', 'Completed', '', 'Call for Service',
                          'Orleans Parish', 'no', 'no', 'other', 'clear conditions', '11 feet to 14 feet', 'yes',
                          'blueteam', 'citizen-uid-5', 'yes', 'no', 'no', 'medium', "5'7'' to 5'9''", '36',
                          'complainant', 'Authorized', 'male', 'black', '37', '3571', 'senior police officer', 'no',
                          '29', '2', '1', 'non-commisioned', 'active', 'FOB - Field Operations Bureau',
                          'Eighth District', 'Narcotics', '', 'Baton Rouge PD']

        self.uof5_dup_data = self.uof5_data.copy()

        self.uofs_data = [
            self.uof1_data,
            self.uof2_data,
            self.uof3_data,
            self.uof4_data,
            self.uof5_data,
            self.uof5_dup_data,
        ]

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    def test_process_successfully(self):
        UseOfForceFactory(uof_uid='uof-uid1')
        UseOfForceFactory(uof_uid='uof-uid2')
        UseOfForceFactory(uof_uid='uof-uid3')

        department_1 = DepartmentFactory(name='New Orleans PD')
        department_2 = DepartmentFactory(name='Baton Rouge PD')

        officer_1 = OfficerFactory(uid='officer-uid1')
        OfficerFactory(uid='officer-uid2')
        officer_3 = OfficerFactory(uid='officer-uid3')

        assert UseOfForce.objects.count() == 3

        WrglRepoFactory(
            data_model=UofImporter.data_model,
            repo_name='uof_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        hash = '3950bd17edfd805972781ef9fe2c6449'

        uof_importer = UofImporter()

        uof_importer.branch = 'main'

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        uof_importer.repo = Mock()
        uof_importer.new_commit = mock_commit

        uof_importer.retrieve_wrgl_data = Mock()

        uof_importer.column_mappings = {column: self.header.index(column) for column in self.header}

        processed_data = {
            'added_rows': [
                self.uof4_data,
                self.uof5_data,
                self.uof5_dup_data
            ],
            'deleted_rows': [
                self.uof3_data,
            ],
            'updated_rows': [
                self.uof1_data,
                self.uof2_data,
            ],
        }

        uof_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = uof_importer.process()

        assert result

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == UofImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 2
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert UseOfForce.objects.count() == 4

        uof_importer.retrieve_wrgl_data.assert_called_with('uof_repo')

        check_columns = self.header + ['department_id', 'officer_id']
        check_columns_mappings = {column: check_columns.index(column) for column in check_columns}

        expected_uof1_data = self.uof1_data.copy()
        expected_uof1_data.append(department_1.id)
        expected_uof1_data.append(officer_1.id)

        expected_uof2_data = self.uof2_data.copy()
        expected_uof2_data.append(None)
        expected_uof2_data.append(None)

        expected_uof4_data = self.uof4_data.copy()
        expected_uof4_data.append(department_1.id)
        expected_uof4_data.append(None)

        expected_uof5_data = self.uof5_data.copy()
        expected_uof5_data.append(department_2.id)
        expected_uof5_data.append(officer_3.id)

        expected_uofs_data = [
            expected_uof1_data,
            expected_uof2_data,
            expected_uof4_data,
            expected_uof5_data,
        ]

        for uof_data in expected_uofs_data:
            uof = UseOfForce.objects.filter(uof_uid=uof_data[check_columns_mappings['uof_uid']]).first()
            assert uof
            field_attrs = [
                'department_id',
                'officer_id',
                'uof_uid',
                'uof_tracking_number',
                'force_description',
                'force_type',
                'force_level',
                'effective_uof',
                'accidental_discharge',
                'less_than_lethal',
                'status',
                'source',
                'service_type',
                'county',
                'traffic_stop',
                'sustained',
                'force_reason',
                'weather_description',
                'distance_from_officer',
                'body_worn_camera_available',
                'app_used',
                'citizen_arrested',
                'citizen_hospitalized',
                'citizen_injured',
                'citizen_body_type',
                'citizen_height',
                'citizen_involvement',
                'disposition',
                'citizen_sex',
                'citizen_race',
                'citizen_age_1',
                'officer_current_supervisor',
                'officer_title',
                'officer_injured',
                'officer_age',
                'officer_type',
                'officer_employment_status',
                'officer_department',
                'officer_division',
                'officer_sub_division_a',
                'officer_sub_division_b',
            ]
            integer_field_attrs = [
                'report_year',
                'citizen_age',
                'officer_years_exp',
                'officer_years_with_unit',
            ]

            for attr in field_attrs:
                assert getattr(uof, attr) == (uof_data[check_columns_mappings[attr]] if uof_data[check_columns_mappings[attr]] else None)

            for attr in integer_field_attrs:
                assert getattr(uof, attr) == (int(uof_data[check_columns_mappings[attr]]) if uof_data[check_columns_mappings[attr]] else None)

    def test_delete_non_existed_uof(self):
        WrglRepoFactory(
            data_model=UofImporter.data_model,
            repo_name='uof_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        hash = '3950bd17edfd805972781ef9fe2c6449'

        uof_importer = UofImporter()

        uof_importer.branch = 'main'

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        uof_importer.repo = Mock()
        uof_importer.new_commit = mock_commit

        uof_importer.retrieve_wrgl_data = Mock()

        uof_importer.column_mappings = {column: self.header.index(column) for column in self.header}

        processed_data = {
            'added_rows': [],
            'deleted_rows': [
                self.uof3_data,
            ],
            'updated_rows': [],
        }

        uof_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = uof_importer.process()

        assert result

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == UofImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 0
        assert import_log.updated_rows == 0
        assert import_log.deleted_rows == 0
        assert not import_log.error_message
        assert import_log.finished_at
