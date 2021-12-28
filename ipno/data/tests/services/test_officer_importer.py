from unittest.mock import MagicMock

from django.test.testcases import TestCase, override_settings

from mock import patch, Mock

from data.services import OfficerImporter
from data.models import ImportLog
from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.factories import WrglRepoFactory
from officers.models import Officer
from officers.factories import OfficerFactory


class OfficerImporterTestCase(TestCase):
    def setUp(self):
        self.header = ['uid', 'last_name', 'middle_name', 'middle_initial', 'first_name', 'birth_year', 'birth_month', 'birth_day', 'race', 'gender']
        self.officer1_data = ['uid1', 'Sanchez', 'C', 'C', 'Emile', '1938', '', '', 'white', 'male']
        self.officer2_data = ['uid2', 'Monaco', 'P', 'P', 'Anthony', '1964', '12', '4', 'black / african american', 'female']
        self.officer3_data = ['uid3', 'Maier', '', '', 'Joel', '', '', '', '', '']
        self.officer4_data = ['uid4', 'Poindexter', 'A', 'A', 'Sylvia', '1973', '', '', '', 'male']
        self.officer5_data = ['uid5', 'Bull', '', '', 'Edward', '', '', '', '', 'male']
        self.officer5_dup_data = ['uid5', 'Bull', '', '', 'Edward', '', '', '', '', 'male']
        self.officer6_data = ['uid6', 'Officer', '', '', 'Deleted', '', '', '', '', 'male']

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    def test_process_successfully(self):
        OfficerFactory(
            uid='uid1',
            first_name='Emile',
            last_name='Sanchez',
        )
        OfficerFactory(
            uid='uid2',
            first_name='Anthony',
            last_name='Monaco',
        )
        OfficerFactory(
            uid='uid3',
            first_name='Joel',
            last_name='Maier',
        )
        OfficerFactory(uid='uid6')

        assert Officer.objects.count() == 4

        WrglRepoFactory(
            data_model=OfficerImporter.data_model,
            repo_name='officer_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        commit_hash = '3950bd17edfd805972781ef9fe2c6449'

        officer_importer = OfficerImporter()

        officer_importer.branch = 'main'

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = commit_hash

        officer_importer.repo = Mock()
        officer_importer.new_commit = mock_commit

        officer_importer.retrieve_wrgl_data = Mock()

        officer_importer.old_column_mappings = {column: self.header.index(column) for column in self.header}
        officer_importer.column_mappings = {column: self.header.index(column) for column in self.header}

        processed_data = {
            'added_rows': [
                self.officer4_data,
                self.officer5_data,
                self.officer5_dup_data,
            ],
            'deleted_rows': [
                self.officer6_data,
            ],
            'updated_rows': [
                self.officer1_data,
                self.officer2_data,
                self.officer3_data,
            ],
        }

        officer_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = officer_importer.process()

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == OfficerImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 3
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Officer.objects.count() == 5

        officer_importer.retrieve_wrgl_data.assert_called_with('officer_repo')

        assert result

        check_columns = officer_importer.column_mappings.copy()

        officers_data = [
            self.officer1_data,
            self.officer2_data,
            self.officer3_data,
            self.officer4_data,
            self.officer5_data,
        ]

        for officer_data in officers_data:
            officer = Officer.objects.filter(uid=officer_data[check_columns['uid']]).first()
            assert officer
            field_attrs = [
                'last_name',
                'middle_name',
                'middle_initial',
                'first_name',
                'race',
                'gender',
            ]
            integer_field_attrs = [
                'birth_year',
                'birth_month',
                'birth_day',
            ]

            for attr in field_attrs:
                assert getattr(officer, attr) == (officer_data[check_columns[attr]] if officer_data[check_columns[attr]] else None)

            for attr in integer_field_attrs:
                assert getattr(officer, attr) == (int(officer_data[check_columns[attr]]) if officer_data[check_columns[attr]] else None)

    def test_get_officer_name_mappings(self):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()

        officer_importer = OfficerImporter()
        result = officer_importer.get_officer_name_mappings()

        expected_result = {
            officer_1.uid: (officer_1.first_name, officer_1.last_name),
            officer_2.uid: (officer_2.first_name, officer_2.last_name),
        }

        assert result == expected_result

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    def test_process_successfully_with_columns_changed(self):
        OfficerFactory(
            uid='uid1',
            first_name='Emile',
            last_name='Sanchez',
        )
        OfficerFactory(
            uid='uid2',
            first_name='Anthony',
            last_name='Monaco',
        )
        OfficerFactory(
            uid='uid3',
            first_name='Joel',
            last_name='Maier',
        )
        OfficerFactory(uid='uid6')

        assert Officer.objects.count() == 4

        WrglRepoFactory(
            data_model=OfficerImporter.data_model,
            repo_name='officer_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        commit_hash = '3950bd17edfd805972781ef9fe2c6449'

        officer_importer = OfficerImporter()

        officer_importer.branch = 'main'

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = commit_hash

        officer_importer.repo = Mock()
        officer_importer.new_commit = mock_commit

        officer_importer.retrieve_wrgl_data = Mock()

        old_columns = self.header[0:4] + self.header[5:]
        officer_importer.old_column_mappings = {column: old_columns.index(column) for column in old_columns}
        officer_importer.column_mappings = {column: self.header.index(column) for column in self.header}

        processed_data = {
            'added_rows': [
                self.officer4_data,
                self.officer5_data,
                self.officer5_dup_data,
            ],
            'deleted_rows': [
                self.officer6_data[0:4] + self.officer6_data[5:],
            ],
            'updated_rows': [
                self.officer1_data,
                self.officer2_data,
                self.officer3_data,
            ],
        }

        officer_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = officer_importer.process()

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == OfficerImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 3
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Officer.objects.count() == 5

        officer_importer.retrieve_wrgl_data.assert_called_with('officer_repo')

        assert result

        check_columns = officer_importer.column_mappings.copy()

        officers_data = [
            self.officer1_data,
            self.officer2_data,
            self.officer3_data,
            self.officer4_data,
            self.officer5_data,
        ]

        for officer_data in officers_data:
            officer = Officer.objects.filter(uid=officer_data[check_columns['uid']]).first()
            assert officer
            field_attrs = [
                'last_name',
                'middle_name',
                'middle_initial',
                'first_name',
                'race',
                'gender',
            ]
            integer_field_attrs = [
                'birth_year',
                'birth_month',
                'birth_day',
            ]

            for attr in field_attrs:
                assert getattr(officer, attr) == (officer_data[check_columns[attr]] if officer_data[check_columns[attr]] else None)

            for attr in integer_field_attrs:
                assert getattr(officer, attr) == (int(officer_data[check_columns[attr]]) if officer_data[check_columns[attr]] else None)

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    def test_process_update_officer_name_successfully(self):
        OfficerFactory(
            uid='uid1',
            first_name='Emile',
            last_name='Sanchez',
            is_name_changed=False,
        )
        OfficerFactory(
            uid='uid2',
            first_name='Anthony',
            last_name='Monac',
            is_name_changed=False,
        )
        OfficerFactory(
            uid='uid3',
            first_name='Maier',
            last_name='Joe',
            is_name_changed=False,
        )
        OfficerFactory(uid='uid6')

        assert Officer.objects.count() == 4

        WrglRepoFactory(
            data_model=OfficerImporter.data_model,
            repo_name='officer_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        commit_hash = '3950bd17edfd805972781ef9fe2c6449'

        officer_importer = OfficerImporter()
        officer_importer.branch = 'main'

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = commit_hash

        officer_importer.repo = Mock()
        officer_importer.new_commit = mock_commit

        officer_importer.retrieve_wrgl_data = Mock()

        officer_importer.old_column_mappings = {column: self.header.index(column) for column in self.header}
        officer_importer.column_mappings = {column: self.header.index(column) for column in self.header}

        processed_data = {
            'added_rows': [
                self.officer4_data,
                self.officer5_data,
                self.officer5_dup_data,
            ],
            'deleted_rows': [
                self.officer6_data,
            ],
            'updated_rows': [
                self.officer1_data,
                self.officer2_data,
                self.officer3_data,
            ],
        }

        officer_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = officer_importer.process()

        assert result

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == OfficerImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 3
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Officer.objects.count() == 5

        check_columns = officer_importer.column_mappings.copy()

        officers_data = [
            self.officer1_data,
            self.officer2_data,
            self.officer3_data,
            self.officer4_data,
            self.officer5_data,
        ]

        for officer_data in officers_data:
            officer = Officer.objects.filter(uid=officer_data[check_columns['uid']]).first()
            assert officer
            field_attrs = [
                'last_name',
                'middle_name',
                'middle_initial',
                'first_name',
                'race',
                'gender',
            ]
            integer_field_attrs = [
                'birth_year',
                'birth_month',
                'birth_day',
            ]

            for attr in field_attrs:
                assert getattr(officer, attr) == (officer_data[check_columns[attr]] if officer_data[check_columns[attr]] else None)

            for attr in integer_field_attrs:
                assert getattr(officer, attr) == (int(officer_data[check_columns[attr]]) if officer_data[check_columns[attr]] else None)

        assert result
        updated_officers = set(Officer.objects.filter(is_name_changed=True).values_list('uid', flat=True))
        expected_uids = ['uid2', 'uid3']
        assert updated_officers == set(expected_uids)

    def test_delete_not_exist_officer(self):
        WrglRepoFactory(
            data_model=OfficerImporter.data_model,
            repo_name='officer_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        commit_hash = '3950bd17edfd805972781ef9fe2c6449'

        officer_importer = OfficerImporter()
        officer_importer.branch = 'main'

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = commit_hash

        officer_importer.repo = Mock()
        officer_importer.new_commit = mock_commit

        officer_importer.retrieve_wrgl_data = Mock()

        officer_importer.old_column_mappings = {column: self.header.index(column) for column in self.header}
        officer_importer.column_mappings = {column: self.header.index(column) for column in self.header}

        processed_data = {
            'added_rows': [],
            'deleted_rows': [
                self.officer6_data,
            ],
            'updated_rows': [],
        }

        officer_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = officer_importer.process()

        assert result

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == OfficerImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 0
        assert import_log.updated_rows == 0
        assert import_log.deleted_rows == 0
        assert not import_log.error_message
        assert import_log.finished_at
