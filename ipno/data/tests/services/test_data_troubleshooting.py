from unittest.mock import MagicMock

from django.test.testcases import TestCase, override_settings

from mock import patch, Mock

from data.factories import WrglRepoFactory
from data.services import DataTroubleshooting
from officers.factories import OfficerFactory
from officers.models import Officer


class DataTroubleshootingCase(TestCase):
    def setUp(self):
        self.header = ['uid', 'last_name', 'middle_name', 'first_name', 'birth_year', 'birth_month', 'birth_day',
                       'race', 'sex']
        self.officer_1 = ['uid1', 'Sanchez', 'C', 'Emile', '1938', '', '', 'white', 'male']
        self.officer_2 = ['uid2', 'Monaco', 'P', 'Anthony', '1964', '12', '4', 'black / african american', 'female']
        self.officer_3 = ['uid3', 'Maier', '', 'Joel', '', '', '', '', '']
        self.officer_4 = ['uid4', 'Poindexter', 'A', 'Sylvia', '1973', '', '', '', 'male']
        self.officer_5 = ['uid5', 'Bull', '', 'Edward', '', '', '', '', 'male']

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.data_troubleshooting.WRGL_USER', 'wrgl_user')
    def test_data_troubleshooting_with_default_input(self):
        data_model = 'Officer'
        OfficerFactory(uid='uid1')
        OfficerFactory(uid='uid2')
        OfficerFactory(uid='uid3')
        OfficerFactory(uid='uid4')
        OfficerFactory(uid='uid5')

        WrglRepoFactory(
            data_model=data_model,
            repo_name='officer_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        commit_hash = '3950bd17edfd805972781ef9fe2c6449'

        data_troubleshooting = DataTroubleshooting()

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = commit_hash

        processed_data = {
            'added_rows': [],
            'deleted_rows': [],
            'updated_rows': [
                self.officer_1,
                self.officer_2,
                self.officer_3,
                self.officer_4,
                self.officer_5,
            ],
        }

        mock_get_blocks = Mock(return_value=processed_data.get('updated_rows'))
        data_troubleshooting.repo = Mock(get_blocks=mock_get_blocks)
        data_troubleshooting.new_commit = mock_commit

        data_troubleshooting.retrieve_wrgl_data = Mock()

        data_troubleshooting.column_mappings = {column: self.header.index(column) for column in self.header}

        data_troubleshooting.process()

        assert Officer.objects.get(uid='uid1').sex == 'male'
        assert Officer.objects.get(uid='uid2').sex == 'female'
        assert Officer.objects.get(uid='uid3').sex == ''
        assert Officer.objects.get(uid='uid4').sex == 'male'
        assert Officer.objects.get(uid='uid5').sex == 'male'

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.data_troubleshooting.WRGL_USER', 'wrgl_user')
    def test_data_troubleshooting(self):
        data_model = 'Officer'
        OfficerFactory(uid='uid1')
        OfficerFactory(uid='uid2')
        OfficerFactory(uid='uid3')
        OfficerFactory(uid='uid4')
        OfficerFactory(uid='uid5')

        WrglRepoFactory(
            data_model=data_model,
            repo_name='officer_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        commit_hash = '3950bd17edfd805972781ef9fe2c6449'

        data_troubleshooting = DataTroubleshooting(
            data_model='Officer',
            updated_fields=['first_name', 'race'],
            table_id='uid'
        )

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = commit_hash

        processed_data = {
            'added_rows': [],
            'deleted_rows': [],
            'updated_rows': [
                self.officer_1,
                self.officer_2,
                self.officer_3,
                self.officer_4,
                self.officer_5,
            ],
        }

        mock_get_blocks = Mock(return_value=processed_data.get('updated_rows'))
        data_troubleshooting.repo = Mock(get_blocks=mock_get_blocks)
        data_troubleshooting.new_commit = mock_commit

        data_troubleshooting.retrieve_wrgl_data = Mock()

        data_troubleshooting.column_mappings = {column: self.header.index(column) for column in self.header}

        data_troubleshooting.process()

        assert Officer.objects.get(uid='uid1').first_name == 'Emile'
        assert Officer.objects.get(uid='uid2').first_name == 'Anthony'
        assert Officer.objects.get(uid='uid3').first_name == 'Joel'
        assert Officer.objects.get(uid='uid4').first_name == 'Sylvia'
        assert Officer.objects.get(uid='uid5').first_name == 'Edward'

        assert Officer.objects.get(uid='uid1').race == 'white'
        assert Officer.objects.get(uid='uid2').race == 'black / african american'
        assert Officer.objects.get(uid='uid3').race == ''
        assert Officer.objects.get(uid='uid4').race == ''
        assert Officer.objects.get(uid='uid5').race == ''

    @patch('data.services.data_troubleshooting.Repository')
    def test_retrieve_wrgl_data(self, mock_repository):
        mock_commit = MagicMock()
        mock_commit.table.columns = ['id', 'name']
        mock_get_branch = Mock(return_value=mock_commit)
        mock_repository.return_value = Mock(get_branch=mock_get_branch)

        data_troubleshooting = DataTroubleshooting()

        data_troubleshooting.retrieve_wrgl_data('branch_name')

        mock_get_branch.assert_called_with('branch_name')
        assert data_troubleshooting.new_commit.table.columns == ['id', 'name']
        assert data_troubleshooting.column_mappings == {
            'id': 0,
            'name': 1
        }
