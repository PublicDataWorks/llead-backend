from unittest.mock import MagicMock

from django.test.testcases import TestCase, override_settings

from mock import patch, Mock

from appeals.factories import AppealFactory
from appeals.models import Appeal
from data.services import AppealImporter
from data.models import ImportLog
from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.factories import WrglRepoFactory
from officers.factories import OfficerFactory
from departments.factories import DepartmentFactory


class AppealImporterTestCase(TestCase):
    def setUp(self):
        self.header = ['appeal_uid', 'docket_no', 'uid', 'counsel', 'charging_supervisor',
                       'appeal_disposition', 'action_appealed', 'appealed', 'agency', 'motions', ]
        self.appeal1_data = ['appeal_uid1', '00-10', 'officer-uid1', 'Dirks', 'Paul Fontenot',
                             'appeal upheld', 'suspension', 'Yes', 'new-orleans-pd', 'amicable settlement']
        self.appeal2_data = ['appeal_uid2', '07-06', 'officer-uid-invalid', 'Falcon', '',
                             'appeal withdrawn', 'dismissed', 'Yes - denied', '',
                             'motion for summary disposition']
        self.appeal3_data = ['appeal_uid3', '07-08', 'officer-uid2', 'Floyd', 'Michael D. Edmonson',
                             'appeal dismissed/denied', 'letter of reprimand', '', 'baton-rouge-pd',
                             'motion to dismiss appeal/failure to prosecute']
        self.appeal4_data = ['appeal_uid4', '11-11', '', 'Floyd', 'Terry C. Landry',
                             'amicable settlement', 'termination', 'No', 'new-orleans-pd',
                             'motion to enforce judgement']
        self.appeal5_data = ['appeal_uid5', '12-05', 'officer-uid3', 'None', 'Stanley Griffin',
                             'denied', 'transfer', '', 'baton-rouge-pd',
                             'motion to enforce decision']

        self.appeal5_dup_data = self.appeal5_data.copy()

        self.appeals_data = [
            self.appeal1_data,
            self.appeal2_data,
            self.appeal3_data,
            self.appeal4_data,
            self.appeal5_data,
            self.appeal5_dup_data,
        ]

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    def test_process_successfully(self):
        AppealFactory(appeal_uid='appeal_uid1')
        AppealFactory(appeal_uid='appeal_uid2')
        AppealFactory(appeal_uid='appeal_uid3')

        department_1 = DepartmentFactory(name='New Orleans PD')
        department_2 = DepartmentFactory(name='Baton Rouge PD')

        officer_1 = OfficerFactory(uid='officer-uid1')
        OfficerFactory(uid='officer-uid2')
        officer_3 = OfficerFactory(uid='officer-uid3')

        assert Appeal.objects.count() == 3

        WrglRepoFactory(
            data_model=AppealImporter.data_model,
            repo_name='appeal_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        hash = '3950bd17edfd805972781ef9fe2c6449'

        appeal_importer = AppealImporter()

        appeal_importer.branch = 'main'

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        appeal_importer.repo = Mock()
        appeal_importer.new_commit = mock_commit

        appeal_importer.retrieve_wrgl_data = Mock()

        appeal_importer.old_column_mappings = {column: self.header.index(column) for column in self.header}
        appeal_importer.column_mappings = {column: self.header.index(column) for column in self.header}

        processed_data = {
            'added_rows': [
                self.appeal4_data,
                self.appeal5_data,
                self.appeal5_dup_data,
            ],
            'deleted_rows': [
                self.appeal3_data,
            ],
            'updated_rows': [
                self.appeal1_data,
                self.appeal2_data,
            ],
        }

        appeal_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = appeal_importer.process()

        assert result

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == AppealImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 2
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Appeal.objects.count() == 4

        appeal_importer.retrieve_wrgl_data.assert_called_with('appeal_repo')

        check_columns = self.header + ['department_id', 'officer_id']
        check_columns_mappings = {column: check_columns.index(column) for column in check_columns}

        expected_appeal1_data = self.appeal1_data.copy()
        expected_appeal1_data.append(department_1.id)
        expected_appeal1_data.append(officer_1.id)

        expected_appeal2_data = self.appeal2_data.copy()
        expected_appeal2_data.append(None)
        expected_appeal2_data.append(None)

        expected_appeal4_data = self.appeal4_data.copy()
        expected_appeal4_data.append(department_1.id)
        expected_appeal4_data.append(None)

        expected_appeal5_data = self.appeal5_data.copy()
        expected_appeal5_data.append(department_2.id)
        expected_appeal5_data.append(officer_3.id)

        expected_appeals_data = [
            expected_appeal1_data,
            expected_appeal2_data,
            expected_appeal4_data,
            expected_appeal5_data,
        ]

        for appeal_data in expected_appeals_data:
            appeal = Appeal.objects.filter(appeal_uid=appeal_data[check_columns_mappings['appeal_uid']]).first()
            assert appeal
            field_attrs = [
                'department_id',
                'officer_id',
                'appeal_uid',
                'docket_no',
                'counsel',
                'charging_supervisor',
                'appeal_disposition',
                'action_appealed',
                'appealed',
                'motions',
            ]

            for attr in field_attrs:
                assert getattr(appeal, attr) == (appeal_data[check_columns_mappings[attr]] if appeal_data[check_columns_mappings[attr]] else None)

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    def test_process_successfully_with_columns_changed(self):
        AppealFactory(appeal_uid='appeal_uid1')
        AppealFactory(appeal_uid='appeal_uid2')
        AppealFactory(appeal_uid='appeal_uid3')

        department_1 = DepartmentFactory(name='New Orleans PD')
        department_2 = DepartmentFactory(name='Baton Rouge PD')

        officer_1 = OfficerFactory(uid='officer-uid1')
        OfficerFactory(uid='officer-uid2')
        officer_3 = OfficerFactory(uid='officer-uid3')

        assert Appeal.objects.count() == 3

        WrglRepoFactory(
            data_model=AppealImporter.data_model,
            repo_name='appeal_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        hash = '3950bd17edfd805972781ef9fe2c6449'

        appeal_importer = AppealImporter()

        appeal_importer.branch = 'main'

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        appeal_importer.repo = Mock()
        appeal_importer.new_commit = mock_commit

        appeal_importer.retrieve_wrgl_data = Mock()

        old_columns = self.header[0:7] + self.header[8:]
        appeal_importer.old_column_mappings = {column: old_columns.index(column) for column in old_columns}
        appeal_importer.column_mappings = {column: self.header.index(column) for column in self.header}

        processed_data = {
            'added_rows': [
                self.appeal4_data,
                self.appeal5_data,
                self.appeal5_dup_data,
            ],
            'deleted_rows': [
                self.appeal3_data[0:7] + self.appeal3_data[8:],
            ],
            'updated_rows': [
                self.appeal1_data,
                self.appeal2_data,
            ],
        }

        appeal_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = appeal_importer.process()

        assert result

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == AppealImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 2
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Appeal.objects.count() == 4

        appeal_importer.retrieve_wrgl_data.assert_called_with('appeal_repo')

        check_columns = self.header + ['department_id', 'officer_id']
        check_columns_mappings = {column: check_columns.index(column) for column in check_columns}

        expected_appeal1_data = self.appeal1_data.copy()
        expected_appeal1_data.append(department_1.id)
        expected_appeal1_data.append(officer_1.id)

        expected_appeal2_data = self.appeal2_data.copy()
        expected_appeal2_data.append(None)
        expected_appeal2_data.append(None)

        expected_appeal4_data = self.appeal4_data.copy()
        expected_appeal4_data.append(department_1.id)
        expected_appeal4_data.append(None)

        expected_appeal5_data = self.appeal5_data.copy()
        expected_appeal5_data.append(department_2.id)
        expected_appeal5_data.append(officer_3.id)

        expected_appeals_data = [
            expected_appeal1_data,
            expected_appeal2_data,
            expected_appeal4_data,
            expected_appeal5_data,
        ]

        for appeal_data in expected_appeals_data:
            appeal = Appeal.objects.filter(appeal_uid=appeal_data[check_columns_mappings['appeal_uid']]).first()
            assert appeal
            field_attrs = [
                'department_id',
                'officer_id',
                'appeal_uid',
                'docket_no',
                'counsel',
                'charging_supervisor',
                'appeal_disposition',
                'action_appealed',
                'appealed',
                'motions',
            ]

            for attr in field_attrs:
                assert getattr(appeal, attr) == (
                    appeal_data[check_columns_mappings[attr]] if appeal_data[check_columns_mappings[attr]] else None)

    def test_delete_non_existed_uof(self):
        DepartmentFactory(name='Baton Rouge PD')
        WrglRepoFactory(
            data_model=AppealImporter.data_model,
            repo_name='uof_appeal',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        hash = '3950bd17edfd805972781ef9fe2c6449'

        appeal_importer = AppealImporter()

        appeal_importer.branch = 'main'

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        appeal_importer.repo = Mock()
        appeal_importer.new_commit = mock_commit

        appeal_importer.retrieve_wrgl_data = Mock()

        appeal_importer.old_column_mappings = {column: self.header.index(column) for column in self.header}
        appeal_importer.column_mappings = {column: self.header.index(column) for column in self.header}

        processed_data = {
            'added_rows': [],
            'deleted_rows': [
                self.appeal3_data,
            ],
            'updated_rows': [],
        }

        appeal_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = appeal_importer.process()

        assert result

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == AppealImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 0
        assert import_log.updated_rows == 0
        assert import_log.deleted_rows == 0
        assert not import_log.error_message
        assert import_log.finished_at
