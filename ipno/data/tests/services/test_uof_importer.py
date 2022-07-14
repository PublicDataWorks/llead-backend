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
        self.header = ['uof_uid', 'tracking_id', 'investigation_status', 'service_type', 'light_condition',
                       'weather_condition', 'shift_time', 'disposition', 'division', 'division_level', 'unit',
                       'originating_bureau', 'agency', 'use_of_force_reason']
        self.uof1_data = ['uof-uid1', 'FTN2015-0705', 'Completed', 'Call for Service', 'good', 'clear conditions',
                          'between 3pm-11pm', 'resolved', 'a platoon', '7th district', 'patrol', 'field operations',
                          'New Orleans PD', 'resisted lawful arrest']
        self.uof2_data = ['uof-uid2', 'FTN2015-0710', '', 'Arresting', 'poor', 'rainy conditions - light',
                          '', 'not sustained', 'b platoon', 'Second District', 'squad a',
                          'FOB - Field Operations Bureau', '', 'flight from an officer']
        self.uof3_data = ['uof-uid3', 'FTN2015-0713', 'Completed', '', 'good', '',
                          'between 7am-3pm', 'exonerated', 'c platoon', '', 'narcotics', 'management services',
                          'Baton Rouge PD', '']
        self.uof4_data = ['uof-uid4', 'FTN2015-07355', 'No', 'Traffic Stop', '', 'other', 'between 3pm-5pm', '',
                          'tactical', '', 'persons', 'Armory Unit', 'New Orleans PD', 'escape']
        self.uof5_data = ['uof-uid5', 'FTN2016-0026', 'Completed', 'Transport', 'good', 'foggy condition',
                          'between 3pm-12am', '', 'a platoon', '', 'patrol', '', 'Baton Rouge PD', 'room clearing']

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

        uof_importer.old_column_mappings = {column: self.header.index(column) for column in self.header}
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

        check_columns = self.header + ['department_id']
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
                'uof_uid',
                'tracking_id',
                'investigation_status',
                'service_type',
                'light_condition',
                'weather_condition',
                'shift_time',
                'disposition',
                'division',
                'division_level',
                'unit',
                'originating_bureau',
                'agency',
                'use_of_force_reason',
            ]

            for attr in field_attrs:
                assert getattr(uof, attr) == (
                    uof_data[check_columns_mappings[attr]] if uof_data[check_columns_mappings[attr]] else None)

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    def test_process_successfully_with_columns_changed(self):
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

        old_columns = self.header[0:7] + self.header[8:]
        uof_importer.old_column_mappings = {column: old_columns.index(column) for column in old_columns}
        uof_importer.column_mappings = {column: self.header.index(column) for column in self.header}

        processed_data = {
            'added_rows': [
                self.uof4_data,
                self.uof5_data,
                self.uof5_dup_data
            ],
            'deleted_rows': [
                self.uof3_data[0:7] + self.uof3_data[8:],
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

        check_columns = self.header + ['department_id']
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
                'uof_uid',
                'tracking_id',
                'investigation_status',
                'service_type',
                'light_condition',
                'weather_condition',
                'shift_time',
                'disposition',
                'division',
                'division_level',
                'unit',
                'originating_bureau',
                'agency',
                'use_of_force_reason',
            ]

            for attr in field_attrs:
                assert getattr(uof, attr) == (
                    uof_data[check_columns_mappings[attr]] if uof_data[check_columns_mappings[attr]] else None)

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

        uof_importer.old_column_mappings = {column: self.header.index(column) for column in self.header}
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
