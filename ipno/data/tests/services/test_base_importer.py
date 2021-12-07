from io import StringIO, BytesIO
from csv import DictWriter
from unittest.mock import MagicMock

from django.test.testcases import TestCase, override_settings
from django.utils.text import slugify

from mock import patch, Mock
from pytest import raises

from data.services import BaseImporter
from data.models import ImportLog
from data.constants import (
    IMPORT_LOG_STATUS_NO_NEW_COMMIT,
    IMPORT_LOG_STATUS_FINISHED,
    IMPORT_LOG_STATUS_ERROR
)
from data.factories import WrglRepoFactory
from departments.factories import DepartmentFactory
from officers.factories import OfficerFactory
from officers.models import Officer
from use_of_forces.factories import UseOfForceFactory
from departments.models import Department


TEST_MODEL_NAME = 'TestModelName'


class TestImporter(BaseImporter):
    data_model = TEST_MODEL_NAME


class BaseImporterTestCase(TestCase):
    def setUp(self):
        csv_content = StringIO()
        writer = DictWriter(
            csv_content,
            fieldnames=['id', 'name']
        )
        writer.writeheader()
        writer.writerows([
            {
                'id': '1',
                'name': 'name 1',
            },
            {
                'id': '2',
                'name': 'name 2',
            },
            {
                'id': '3',
                'name': 'name 3',
            },
        ])
        self.csv_stream = BytesIO(csv_content.getvalue().encode('utf-8'))
        self.csv_text = csv_content.getvalue()
        self.tbi = TestImporter()

    def test_process_wrgl_repo_not_found(self):
        assert not TestImporter().process()

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == TEST_MODEL_NAME
        assert import_log.status == IMPORT_LOG_STATUS_ERROR
        assert import_log.error_message == 'Cannot find Wrgl Repo!'
        assert import_log.finished_at

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    def test_process_invalid_wrgl_repo_name(self):
        WrglRepoFactory(
            data_model=TEST_MODEL_NAME,
            repo_name='test_repo_name'
        )

        self.tbi.branch = 'main'

        mock_commit = MagicMock()
        mock_commit.table.columns = ['id', 'uid']
        mock_commit.sum = ''

        self.tbi.repo = Mock()
        self.tbi.new_commit = mock_commit

        self.tbi.retrieve_wrgl_data = Mock()

        assert not self.tbi.process()

        self.tbi.retrieve_wrgl_data.assert_called_with('test_repo_name')

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == TEST_MODEL_NAME
        assert import_log.status == IMPORT_LOG_STATUS_ERROR
        assert import_log.error_message == 'Cannot get latest commit hash from Wrgl for repo test_repo_name!'
        assert import_log.finished_at

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    def test_process_no_new_commit(self):
        WrglRepoFactory(
            data_model=TEST_MODEL_NAME,
            repo_name='test_repo_name',
            commit_hash='3950bd17edfd805972781ef9fe2c6449'
        )

        hash = '3950bd17edfd805972781ef9fe2c6449'

        self.tbi.branch = 'main'

        mock_commit = MagicMock()
        mock_commit.table.columns = ['id', 'uid']
        mock_commit.sum = hash

        self.tbi.repo = Mock()
        self.tbi.new_commit = mock_commit

        self.tbi.retrieve_wrgl_data = Mock()

        assert not self.tbi.process()

        self.tbi.retrieve_wrgl_data.assert_called_with('test_repo_name')

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == TEST_MODEL_NAME
        assert import_log.status == IMPORT_LOG_STATUS_NO_NEW_COMMIT
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert not import_log.error_message
        assert import_log.finished_at

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    def test_process_error_while_processing_data(self):
        WrglRepoFactory(
            data_model=TEST_MODEL_NAME,
            repo_name='test_repo_name',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        hash = '3950bd17edfd805972781ef9fe2c6449'

        self.tbi.branch = 'main'

        mock_commit = MagicMock()
        mock_commit.table.columns = ['id', 'uid']
        mock_commit.sum = hash

        self.tbi.repo = Mock()
        self.tbi.new_commit = mock_commit

        self.tbi.retrieve_wrgl_data = Mock()

        self.tbi.import_data = Exception()

        assert not self.tbi.process()

        assert self.tbi.retrieve_wrgl_data('test_repo_name')

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == TEST_MODEL_NAME
        assert import_log.status == IMPORT_LOG_STATUS_ERROR
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert 'Error occurs while importing data!' in import_log.error_message
        assert import_log.finished_at

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    def test_process_successfully(self):
        WrglRepoFactory(
            data_model=TEST_MODEL_NAME,
            repo_name='test_repo_name',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        import_data_result = {
            'created_rows': 2,
            'updated_rows': 0,
            'deleted_rows': 1,
        }

        hash = '3950bd17edfd805972781ef9fe2c6449'

        self.tbi.branch = 'main'

        mock_commit = MagicMock()
        mock_commit.table.columns = ['id', 'name']
        mock_commit.sum = hash

        self.tbi.repo = Mock()
        self.tbi.new_commit = mock_commit

        self.tbi.retrieve_wrgl_data = Mock()

        self.tbi.import_data = Mock(return_value=import_data_result)

        processed_data = {
            'added_rows': [
                ['1', 'name 1'],
                ['3', 'name 3']
            ],
            'deleted_rows': [
                ['2', 'name 2'],
            ],
            'updated_rows': [],
        }

        self.tbi.process_wrgl_data = Mock(return_value=processed_data)

        assert self.tbi.process()

        assert self.tbi.retrieve_wrgl_data('test_repo_name')

        self.tbi.import_data.assert_called_with(processed_data)

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == TEST_MODEL_NAME
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 0
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    def test_process_successfully_without_current_commit_hash(self):
        WrglRepoFactory(
            data_model=TEST_MODEL_NAME,
            repo_name='test_repo_name',
            commit_hash=''
        )

        import_data_result = {
            'created_rows': 2,
            'updated_rows': 0,
            'deleted_rows': 0,
        }

        hash = '3950bd17edfd805972781ef9fe2c6449'

        self.tbi.branch = 'main'

        mock_commit = MagicMock()
        mock_commit.table.columns = ['id', 'name']
        mock_commit.table.sum = hash
        mock_commit.sum = hash

        self.tbi.new_commit = mock_commit

        self.tbi.retrieve_wrgl_data = Mock()

        self.tbi.import_data = Mock(return_value=import_data_result)

        processed_data = {
            'added_rows': [
                ['1', 'name 1'],
                ['3', 'name 3']
            ],
            'deleted_rows': [],
            'updated_rows': [],
        }

        self.tbi.process_wrgl_data = Mock()

        mock_get_blocks = Mock(return_value=processed_data.get('added_rows'))
        self.tbi.repo = Mock(get_blocks=mock_get_blocks)

        assert self.tbi.process()

        assert self.tbi.retrieve_wrgl_data('test_repo_name')

        self.tbi.process_wrgl_data.assert_not_called()
        self.tbi.repo.get_blocks.assert_called_with(
            'heads/main',
            with_column_names=False
        )
        self.tbi.import_data.assert_called_with(processed_data)

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == TEST_MODEL_NAME
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 0
        assert import_log.deleted_rows == 0
        assert not import_log.error_message
        assert import_log.finished_at

    @patch('data.services.base_importer.Repository')
    def test_retrieve_wrgl_data(self, mock_repository):
        mock_commit = MagicMock()
        mock_commit.table.columns = ['id', 'name']
        mock_get_branch = Mock(return_value=mock_commit)
        mock_repository.return_value = Mock(get_branch=mock_get_branch)

        self.tbi.branch = 'main'
        self.tbi.retrieve_wrgl_data('dummy')

        mock_get_branch.assert_called_with('main')
        assert self.tbi.new_commit.table.columns == ['id', 'name']
        assert self.tbi.column_mappings == {
            'id': 0,
            'name': 1
        }

    def test_import_data(self):
        with raises(NotImplementedError):
            BaseImporter().import_data([])

    def test_format_agency(self):
        assert BaseImporter().format_agency('Baton Rouge CSD') == 'Baton Rouge PD'
        assert BaseImporter().format_agency('Baton Rouge SO') == 'Baton Rouge Sheriff'

    def test_department_mappings(self):
        department_1 = DepartmentFactory(name='New Orleans PD')
        department_2 = DepartmentFactory(name='Baton Rouge PD')
        agencies = ['St. Tammany Sheriff', 'Baton Rouge CSD', 'New Orleans PD']

        mappings = BaseImporter().get_department_mappings(agencies)

        department_3 = Department.objects.filter(name='St. Tammany Sheriff').first()
        expected_mappings = {
            slugify('New Orleans PD'): department_1.id,
            slugify('Baton Rouge PD'): department_2.id,
            slugify('St. Tammany Sheriff'): department_3.id
        }
        assert department_3
        assert mappings == expected_mappings

    def test_department_mappings_case_sensitive(self):
        department_1 = DepartmentFactory(name='New Orleans PD')
        agencies = ['St. Tammany Sheriff', 'New Orleans PD', 'st. tammany sheriff']

        mappings = BaseImporter().get_department_mappings(agencies)

        department_2 = Department.objects.filter(name='St. Tammany Sheriff').first()
        expected_mappings = {
            slugify('New Orleans PD'): department_1.id,
            slugify('St. Tammany Sheriff'): department_2.id
        }
        assert department_2
        assert mappings == expected_mappings

    def test_department_mappings_change_department_name(self):
        department_1 = DepartmentFactory(name='New Orleans PD')
        department_2 = DepartmentFactory(name='Baton Rouge PD')
        agencies = ['St. Tammany Sheriff', 'Baton Rouge CSD', 'New Orleans PD']

        mappings = BaseImporter().get_department_mappings(agencies)

        department_1.name = 'New Orleans Police Department'
        department_1.save()
        department_2.name = 'Baton Rouge Police Department'
        department_2.save()

        new_mappings = BaseImporter().get_department_mappings(agencies)

        department_3 = Department.objects.filter(name='St. Tammany Sheriff').first()
        expected_mappings = {
            slugify('New Orleans PD'): department_1.id,
            slugify('Baton Rouge PD'): department_2.id,
            slugify('St. Tammany Sheriff'): department_3.id
        }
        assert department_3
        assert mappings == expected_mappings
        assert mappings == new_mappings

    def test_officer_mappings(self):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        mappings = BaseImporter().get_officer_mappings()
        expected_mappings = {
            officer_1.uid: officer_1.id,
            officer_2.uid: officer_2.id,
        }

        assert mappings == expected_mappings

    def test_uof_mappings(self):
        uof_1 = UseOfForceFactory()
        uof_2 = UseOfForceFactory()
        mappings = BaseImporter().get_uof_mappings()
        expected_mappings = {
            uof_1.uof_uid: uof_1.id,
            uof_2.uof_uid: uof_2.id,
        }

        assert mappings == expected_mappings

    def test_parse_row_data(self):
        self.tbi.ATTRIBUTES = ['id', 'name', 'year', 'desc', 'uid']
        self.tbi.NA_ATTRIBUTES = ['desc']
        self.tbi.INT_ATTRIBUTES = ['year']

        self.tbi.column_mappings = {
            'id': 0,
            'name': 1,
            'year': 2,
            'desc': 3
        }

        row = ['1', 'test', '2021', 'NA']

        result = self.tbi.parse_row_data(row)

        expected_result = {
            'id': '1',
            'name': 'test',
            'year': 2021,
            'desc': None
        }

        assert result == expected_result

    def test_get_all_diff_rows(self):
        raw_data = {
            'added_rows': [
                ['1', 'name 1'],
            ],
            'deleted_rows': [
                ['2', 'name 2'],
            ],
            'updated_rows': [
                ['3', 'name 3']
            ],
        }

        result = self.tbi.get_all_diff_rows(raw_data)

        assert result == [
            ['1', 'name 1'],
            ['2', 'name 2'],
            ['3', 'name 3']
        ]

    def test_process_wrgl_data(self):
        mock_rows = [
            Mock(off1=1, off2=None),
            Mock(off1=None, off2=2),
            Mock(off1=3, off2=3)
        ]
        mock_diff = Mock(return_value=Mock(row_diff=mock_rows))
        mock_get_commit = Mock()
        mock_get_table_rows = Mock()

        def mock_get_table_rows_side_effect(table_sum, offs):
            if 1 in offs:
                return [['id1', 'name1']]
            elif 2 in offs:
                return [['id2', 'name2']]
            else:
                return [['id3', 'name3']]
        mock_get_table_rows.side_effect = mock_get_table_rows_side_effect

        self.tbi.repo = Mock(
            diff=mock_diff,
            get_commit=mock_get_commit,
            get_table_rows=mock_get_table_rows
        )
        self.tbi.new_commit = Mock(sum='new_commit_hash')

        old_commit_hash = 'dummy-old-commit-hash'
        result = self.tbi.process_wrgl_data(old_commit_hash)

        mock_diff.assert_called_with('new_commit_hash', 'dummy-old-commit-hash')
        mock_get_commit.assert_called_with('dummy-old-commit-hash')

        expected_result = {
            'added_rows': [['id1', 'name1']],
            'deleted_rows': [['id2', 'name2']],
            'updated_rows': [['id3', 'name3']],
        }

        assert result == expected_result

    def test_bulk_import(self):
        OfficerFactory()
        officer_2 = OfficerFactory()
        officer_3 = OfficerFactory()

        new_items_attrs = [{
            'uid': 'abc',
            'first_name': 'test_1',
        }]

        self.tbi.UPDATE_ATTRIBUTES = ['first_name']

        update_items_attrs = [{
            'id': officer_3.id,
            'first_name': 'test_2',
        }]

        delete_items_ids = [officer_2.id]

        result = self.tbi.bulk_import(Officer, new_items_attrs, update_items_attrs, delete_items_ids)

        expected_result = {
            'created_rows': 1,
            'updated_rows': 1,
            'deleted_rows': 1
        }

        assert result == expected_result

    def test_bulk_import_with_cleanup_action(self):
        OfficerFactory()
        officer_2 = OfficerFactory()
        officer_3 = OfficerFactory()

        new_items_attrs = [{
            'uid': 'abc',
            'first_name': 'test_1',
        }]

        self.tbi.UPDATE_ATTRIBUTES = ['first_name']

        update_items_attrs = [{
            'id': officer_3.id,
            'first_name': 'test_2',
        }]

        delete_items_ids = [officer_2.id]

        cleanup_action = Mock()

        delete_items_values = list(Officer.objects.filter(id__in=[officer_2.id]).values())

        result = self.tbi.bulk_import(Officer, new_items_attrs, update_items_attrs, delete_items_ids, cleanup_action)

        expected_result = {
            'created_rows': 1,
            'updated_rows': 1,
            'deleted_rows': 1
        }

        assert result == expected_result

        cleanup_action.assert_called_with(delete_items_values)
