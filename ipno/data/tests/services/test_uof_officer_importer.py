from unittest.mock import MagicMock

from django.test.testcases import TestCase, override_settings

from mock import patch, Mock

from data.services import UofOfficerImporter
from data.models import ImportLog
from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.factories import WrglRepoFactory
from officers.factories import OfficerFactory
from use_of_forces.factories import UseOfForceOfficerFactory, UseOfForceFactory
from use_of_forces.models import UseOfForceOfficer


class UofOfficerImporterTestCase(TestCase):
    def setUp(self):
        self.header = ['uof_uid', 'uid', 'use_of_force_type', 'use_of_force_level', 'use_of_force_effective', 'age',
                       'years_of_service', 'officer_injured']
        self.uof_officer_1_data = ['uof-uid1', 'officer-uid2', 'firearm', 'l1', 'yes', 28, 5, 'no']
        self.uof_officer_2_data = ['uof-uid2', 'officer-uid3', '', 'l2', 'yes', 30, None, '']
        self.uof_officer_3_data = ['uof-uid3', 'officer-uid3', 'hands', '', '', 30, 4, 'yes']
        self.uof_officer_4_data = ['uof-uid4', 'officer-uid4', 'takedown', 'l4', 'no', None, None, 'yes']
        self.uof_officer_5_data = ['uof-uid4', 'officer-uid1', '', 'l4', '', None, 8, 'no']

        self.uof_officer_4_dup_data = self.uof_officer_4_data.copy()

        self.uof_officers_data = [
            self.uof_officer_1_data,
            self.uof_officer_2_data,
            self.uof_officer_3_data,
            self.uof_officer_4_data,
            self.uof_officer_4_dup_data,
            self.uof_officer_5_data,
        ]

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    def test_process_successfully(self):
        officer_1 = OfficerFactory(uid='officer-uid1')
        officer_2 = OfficerFactory(uid='officer-uid2')
        officer_3 = OfficerFactory(uid='officer-uid3')
        officer_4 = OfficerFactory(uid='officer-uid4')

        use_of_force_1 = UseOfForceFactory(uof_uid='uof-uid1')
        use_of_force_2 = UseOfForceFactory(uof_uid='uof-uid2')
        use_of_force_3 = UseOfForceFactory(uof_uid='uof-uid3')
        use_of_force_4 = UseOfForceFactory(uof_uid='uof-uid4')

        UseOfForceOfficerFactory(uof_uid='uof-uid1', uid='officer-uid3', officer=officer_3, use_of_force=use_of_force_1)
        UseOfForceOfficerFactory(uof_uid='uof-uid1', uid='officer-uid2', officer=officer_2, use_of_force=use_of_force_1)
        UseOfForceOfficerFactory(uof_uid='uof-uid2', uid='officer-uid3', officer=officer_3, use_of_force=use_of_force_2)
        UseOfForceOfficerFactory(uof_uid='uof-uid4', uid='officer-uid1', officer=officer_1, use_of_force=use_of_force_4)

        assert UseOfForceOfficer.objects.count() == 4
        assert list(use_of_force_1.officers.all()) == [officer_3, officer_2]
        assert list(officer_3.use_of_forces.all()) == [use_of_force_1, use_of_force_2]

        WrglRepoFactory(
            data_model=UofOfficerImporter.data_model,
            repo_name='uof_officer_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        hash = '3950bd17edfd805972781ef9fe2c6449'

        uof_officer_importer = UofOfficerImporter()

        uof_officer_importer.branch = 'main'

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        uof_officer_importer.repo = Mock()
        uof_officer_importer.new_commit = mock_commit

        uof_officer_importer.retrieve_wrgl_data = Mock()

        uof_officer_importer.old_column_mappings = {column: self.header.index(column) for column in self.header}
        uof_officer_importer.column_mappings = {column: self.header.index(column) for column in self.header}

        processed_data = {
            'added_rows': [
                self.uof_officer_3_data,
                self.uof_officer_4_data,
                self.uof_officer_4_dup_data
            ],
            'deleted_rows': [
                self.uof_officer_1_data,
                self.uof_officer_2_data,
            ],
            'updated_rows': [
                self.uof_officer_5_data,
            ],
        }

        uof_officer_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = uof_officer_importer.process()

        assert result

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == UofOfficerImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 1
        assert import_log.deleted_rows == 2
        assert not import_log.error_message
        assert import_log.finished_at

        assert UseOfForceOfficer.objects.count() == 4

        assert list(use_of_force_1.officers.all()) == [officer_3]
        assert list(officer_3.use_of_forces.all()) == [use_of_force_1, use_of_force_3]

        uof_officer_importer.retrieve_wrgl_data.assert_called_with('uof_officer_repo')

        check_columns = self.header + ['officer_id', 'use_of_force_id']
        check_columns_mappings = {column: check_columns.index(column) for column in check_columns}

        expected_uof_officer_3_data = self.uof_officer_3_data.copy()
        expected_uof_officer_3_data.append(officer_3.id)
        expected_uof_officer_3_data.append(use_of_force_3.id)

        expected_uof_officer_4_data = self.uof_officer_4_data.copy()
        expected_uof_officer_4_data.append(officer_4.id)
        expected_uof_officer_4_data.append(use_of_force_4.id)

        expected_uof_officer_5_data = self.uof_officer_5_data.copy()
        expected_uof_officer_5_data.append(officer_1.id)
        expected_uof_officer_5_data.append(use_of_force_4.id)

        expected_uof_officers_data = [
            expected_uof_officer_3_data,
            expected_uof_officer_4_data,
            expected_uof_officer_5_data,
        ]

        for uof_office_data in expected_uof_officers_data:
            uof_officer = UseOfForceOfficer.objects.filter(
                uid=uof_office_data[check_columns_mappings['uid']],
                uof_uid=uof_office_data[check_columns_mappings['uof_uid']],
            ).first()
            assert uof_officer

            field_attrs = [
                'uof_uid',
                'uid',
                'use_of_force_type',
                'use_of_force_level',
                'use_of_force_effective',
                'age',
                'years_of_service',
                'officer_injured',
                'officer_id',
                'use_of_force_id',
            ]

            for attr in field_attrs:
                assert getattr(uof_officer, attr) == (
                    uof_office_data[check_columns_mappings[attr]]
                    if uof_office_data[check_columns_mappings[attr]]
                    else None
                )

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    def test_process_successfully_with_columns_changed(self):
        officer_1 = OfficerFactory(uid='officer-uid1')
        officer_2 = OfficerFactory(uid='officer-uid2')
        officer_3 = OfficerFactory(uid='officer-uid3')
        officer_4 = OfficerFactory(uid='officer-uid4')

        use_of_force_1 = UseOfForceFactory(uof_uid='uof-uid1')
        use_of_force_2 = UseOfForceFactory(uof_uid='uof-uid2')
        use_of_force_3 = UseOfForceFactory(uof_uid='uof-uid3')
        use_of_force_4 = UseOfForceFactory(uof_uid='uof-uid4')

        UseOfForceOfficerFactory(uof_uid='uof-uid1', uid='officer-uid3', officer=officer_3, use_of_force=use_of_force_1)
        UseOfForceOfficerFactory(uof_uid='uof-uid1', uid='officer-uid2', officer=officer_2, use_of_force=use_of_force_1)
        UseOfForceOfficerFactory(uof_uid='uof-uid2', uid='officer-uid3', officer=officer_3, use_of_force=use_of_force_2)
        UseOfForceOfficerFactory(uof_uid='uof-uid4', uid='officer-uid1', officer=officer_1, use_of_force=use_of_force_4)

        assert UseOfForceOfficer.objects.count() == 4
        assert list(use_of_force_1.officers.all()) == [officer_3, officer_2]
        assert list(officer_3.use_of_forces.all()) == [use_of_force_1, use_of_force_2]

        WrglRepoFactory(
            data_model=UofOfficerImporter.data_model,
            repo_name='uof_officer_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        hash = '3950bd17edfd805972781ef9fe2c6449'

        uof_officer_importer = UofOfficerImporter()

        uof_officer_importer.branch = 'main'

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        uof_officer_importer.repo = Mock()
        uof_officer_importer.new_commit = mock_commit

        uof_officer_importer.retrieve_wrgl_data = Mock()

        old_columns = self.header[0:7] + self.header[8:]
        uof_officer_importer.old_column_mappings = {column: old_columns.index(column) for column in old_columns}
        uof_officer_importer.column_mappings = {column: self.header.index(column) for column in self.header}

        processed_data = {
            'added_rows': [
                self.uof_officer_3_data,
                self.uof_officer_4_data,
                self.uof_officer_4_dup_data
            ],
            'deleted_rows': [
                self.uof_officer_1_data,
                self.uof_officer_2_data,
            ],
            'updated_rows': [
                self.uof_officer_5_data,
            ],
        }

        uof_officer_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = uof_officer_importer.process()

        assert result

        import_log = ImportLog.objects.order_by('-created_at').last()

        assert import_log.data_model == UofOfficerImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 1
        assert import_log.deleted_rows == 2
        assert not import_log.error_message
        assert import_log.finished_at

        assert UseOfForceOfficer.objects.count() == 4

        uof_officer_importer.retrieve_wrgl_data.assert_called_with('uof_officer_repo')

        check_columns = self.header + ['officer_id', 'use_of_force_id']
        check_columns_mappings = {column: check_columns.index(column) for column in check_columns}

        expected_uof_officer_3_data = self.uof_officer_3_data.copy()
        expected_uof_officer_3_data.append(officer_3.id)
        expected_uof_officer_3_data.append(use_of_force_3.id)

        expected_uof_officer_4_data = self.uof_officer_4_data.copy()
        expected_uof_officer_4_data.append(officer_4.id)
        expected_uof_officer_4_data.append(use_of_force_4.id)

        expected_uof_officer_5_data = self.uof_officer_5_data.copy()
        expected_uof_officer_5_data.append(officer_1.id)
        expected_uof_officer_5_data.append(use_of_force_4.id)

        expected_uof_officers_data = [
            expected_uof_officer_3_data,
            expected_uof_officer_4_data,
            expected_uof_officer_5_data,
        ]

        for uof_office_data in expected_uof_officers_data:
            uof_officer = UseOfForceOfficer.objects.filter(
                uid=uof_office_data[check_columns_mappings['uid']],
                uof_uid=uof_office_data[check_columns_mappings['uof_uid']],
            ).first()
            assert uof_officer

            field_attrs = [
                'uof_uid',
                'uid',
                'use_of_force_type',
                'use_of_force_level',
                'use_of_force_effective',
                'age',
                'years_of_service',
                'officer_injured',
                'officer_id',
                'use_of_force_id',
            ]

            for attr in field_attrs:
                assert getattr(uof_officer, attr) == (
                    uof_office_data[check_columns_mappings[attr]]
                    if uof_office_data[check_columns_mappings[attr]]
                    else None
                )

    def test_delete_non_existed_uof(self):
        WrglRepoFactory(
            data_model=UofOfficerImporter.data_model,
            repo_name='uof_officer_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        hash = '3950bd17edfd805972781ef9fe2c6449'

        uof_officer_importer = UofOfficerImporter()

        uof_officer_importer.branch = 'main'

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        uof_officer_importer.repo = Mock()
        uof_officer_importer.new_commit = mock_commit

        uof_officer_importer.retrieve_wrgl_data = Mock()

        uof_officer_importer.old_column_mappings = {column: self.header.index(column) for column in self.header}
        uof_officer_importer.column_mappings = {column: self.header.index(column) for column in self.header}

        processed_data = {
            'added_rows': [],
            'deleted_rows': [
                self.uof_officer_3_data,
            ],
            'updated_rows': [],
        }

        uof_officer_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = uof_officer_importer.process()

        assert result

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == UofOfficerImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 0
        assert import_log.updated_rows == 0
        assert import_log.deleted_rows == 0
        assert not import_log.error_message
        assert import_log.finished_at
