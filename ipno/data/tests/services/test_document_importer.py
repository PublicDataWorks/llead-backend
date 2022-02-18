from inspect import cleandoc

from django.test.testcases import TestCase, override_settings
from django.conf import settings
from django.utils.text import slugify
from unittest.mock import call, ANY
from mock import patch, Mock, MagicMock


from dropbox.exceptions import ApiError

from data.services import DocumentImporter
from data.models import ImportLog
from data.constants import IMPORT_LOG_STATUS_FINISHED, IMPORT_LOG_STATUS_ERROR
from data.factories import WrglRepoFactory
from documents.models import Document
from documents.factories import DocumentFactory
from officers.factories import OfficerFactory
from departments.factories import DepartmentFactory


class DocumentImporterTestCase(TestCase):
    def setUp(self):
        self.patcher = patch('data.services.document_importer.GoogleCloudService')
        self.patcher.start()

        self.header = ['docid', 'page_count', 'fileid', 'title', 'pdf_db_path', 'pdf_db_content_hash', 'txt_db_id',
                       'txt_db_content_hash', 'year', 'month', 'day', 'dt_source', 'hrg_no', 'accused', 'matched_uid',
                       'agency', 'hrg_text', 'hrg_type']
        self.document1_data = [
            '00fa809e', '4', 'f0fcc0d', 'document 1 title',
            '/PPACT/meeting-minutes-extraction/export/pdfs/00fa809e.pdf',
            'ceb9779f43154497099356c8bd74cacce1faa780cb6916a85efc8b4e278a776c',
            'id:8ceKnrnmgi0AAAAAAAAqmQ',
            'e8a785ca3624bce9fe76a630fd6dbf07ab194202ef135480c76d9dbee79ab8ff', '2018', '6', '14',
            'scraped', '1', 'Joseph Jones, Docket No. 17-', 'officer-uid-1', 'New Orleans PD',
            cleandoc("""
                   3. Discussion of Subpoenas Requested in the Appeal of Joseph Jones, Docket No. 17-
                   237-S
                   Lenore Feeney, State Police Commission Referee, advised that the hearing has been
                   set for August 9, 2018, and noted that the majority of subpoenas issued for this
                   hearing are to persons residing in the Monroe area.
                   On motion duly made by Mr. Riecke, seconded, and unanimously passed, the
                   Commission voted to move the Commission hearing as well as the regular public
                   meeting to a suitable location in Monroe on August 9, 2018.
                   In Favor: All
                   Opposed: None
                   SPC Minutes, 6/14/2018, pg. 3
           """),
            "police"
        ]
        self.document2_data = [
            '0236e725', '1', 'd4fb65b', 'document 2 title',
            '/PPACT/meeting-minutes-extraction/export/pdfs/0236e725.pdf',
            '5f05f28383649aad924c89627c864c615856974d22f2eb53a6bdcf4464c76d20',
            'id:8ceKnrnmgi0AAAAAAAAqmw',
            '2c668256378a491fd2f2812fcd4fc0f22af292b66f3f63ce6070321c57497f5a', '2018', '12', '18',
            'scraped', '1', 'Officer Terry Guillory, Docket 17-201', 'officer-uid-2', '', '', 'unknown']
        self.document3_data = [
            '0dd28391', '3', '77d489c', 'document 3 title',
            '/PPACT/meeting-minutes-extraction/export/pdfs/0dd28391.pdf',
            'a3847e1c769816a9988f90fa02b77c9c9a239f48684b9ff2b6cbe134cb59a14c',
            'id:8ceKnrnmgi0AAAAAAAAqng',
            'affc812dbf419a261ba5edd110c7abef90a0a3e7ee0ec285b1e90cba2f7680a7', '1999', '9', '30',
            'scraped', '1', 'WILLIAM C. BROWN', 'officer-uid-3', 'Baton Rouge PD',
            cleandoc("""
               APPEAL HEARING FOR WILLIAM C. BROWN
               Mr. William C. Brown submitted a request to withdraw his appeal. A motion was made by
               Henry Clark to accept this request for withdrawal and seconded by Lyle Johnson. Motion
               approved unanimously.
           """),
            "fire"
        ]
        self.document4_data = [
            '0dd28391', '3', '77d489c', 'document 4 title',
            '/PPACT/meeting-minutes-extraction/export/pdfs/0dd28391.pdf',
            'a3847e1c769816a9988f90fa02b77c9c9a239f48684b9ff2b6cbe134cb59a14c',
            'id:8ceKnrnmgi0AAAAAAAAqng',
            'affc812dbf419a261ba5edd110c7abef90a0a3e7ee0ec285b1e90cba2f7680a7', '1999', '9', '30',
            'scraped', '2', 'JIM VERLANDER', '', 'New Orleans PD',
            cleandoc("""
               APPEAL HEARING FOR JIM VERLANDER
               Mr. Verlander has submitted a letter stating that an agreement has been reached between
               himself and Chief Phares. Board asks that Ms. Johnson make sure that a Personnel Action
               form is received from Chief Phares regarding the agreement.
               Cynthia Wilkinson made a motion to accept the letter tentatively until a Personnel Action
               form is received from Chief Phares regarding the agreement. This motion was seconded by
               Lyle Johnson. Motion approved unanimously.
           """),
            "unknown"
        ]
        self.document5_data = [
            '0dd28391', '3', '77d489c', 'document 5 title',
            '/PPACT/meeting-minutes-extraction/export/pdfs/0dd28391.pdf',
            'a3847e1c769816a9988f90fa02b77c9c9a239f48684b9ff2b6cbe134cb59a14c',
            'id:8ceKnrnmgi0AAAAAAAAqng',
            'affc812dbf419a261ba5edd110c7abef90a0a3e7ee0ec285b1e90cba2f7680a7', '1999', '9', '30',
            'scraped', '3', 'OFFICER KEVIN LAPEYROUSE', '', '', '', 'fire']

        self.document6_data = [
            '0dd82391', '3', '77d489c', 'document 5 title',
            '/PPACT/meeting-minutes-extraction/export/pdfs/0dd28391.pdf',
            'a3847e1c769816a9988f90fa02b77c9c9a239f48684b9ff2b6cbe134cb59a14c',
            'id:8ceKnrnmgi0AAAAAAAAqng',
            'affc812dbf419a261ba5edd110c7abef90a0a3e7ee0ec285b1e90cba2f7680a7', '1999', '9', '30',
            'scraped', '3', 'OFFICER KEVIN LAPEYROUSE', '', '', 'new-orleans-pd', 'unknown']

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    def test_process_fail_dueto_dropbox_get_file_error(self):
        WrglRepoFactory(
            data_model=DocumentImporter.data_model,
            repo_name='document_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        commit_hash = '87d27e0616d9ef342e1728f5533162a3'

        document_importer = DocumentImporter()

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = commit_hash

        document_importer.repo = Mock()
        document_importer.new_commit = mock_commit

        document_importer.retrieve_wrgl_data = Mock()

        document_importer.old_column_mappings = {column: self.header.index(column) for column in self.header}
        document_importer.column_mappings = {column: self.header.index(column) for column in self.header}

        processed_data = {
            'added_rows': [
                self.document2_data,
                self.document4_data,
            ],
            'deleted_rows': [
                self.document3_data,
            ],
            'updated_rows': [
                self.document1_data,
                self.document5_data,
            ],
        }

        document_importer.process_wrgl_data = Mock(return_value=processed_data)

        def upload_file_side_effect(upload_location, _file_blob, _file_type):
            return f"{settings.GC_PATH}{upload_location}".replace(' ', '%20').replace("'", '%27')

        mock_upload_file = MagicMock(side_effect=upload_file_side_effect)
        document_importer.upload_file = mock_upload_file

        api_error = ApiError(
            request_id=1,
            error='error',
            user_message_text='user_message_text',
            user_message_locale='user_message_locale'
        )
        mock_get_temporary_link_from_path = Mock(side_effect=api_error)
        document_importer.ds = Mock(get_temporary_link_from_path=mock_get_temporary_link_from_path)

        document_importer.process()
        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == 'Document'
        assert import_log.status == IMPORT_LOG_STATUS_ERROR
        assert 'Error downloading dropbox file from path:' in import_log.error_message
        assert import_log.finished_at

    def test_upload_file_success(self):
        upload_location = 'location'
        file_blob = 'file_blob'
        file_type = 'file_type'

        mock_upload_file_from_string = MagicMock()
        document_importer = DocumentImporter()
        document_importer.gs = MagicMock(upload_file_from_string=mock_upload_file_from_string)

        download_url = document_importer.upload_file(upload_location, file_blob, file_type)

        mock_upload_file_from_string.assert_called_with(upload_location, file_blob, file_type)

        assert download_url == f'{settings.GC_PATH}location'

    def test_upload_file_success_in_development(self):
        upload_location = 'location'
        file_blob = 'file_blob'
        file_type = 'file_type'

        mock_upload_file_from_string = MagicMock()
        document_importer = DocumentImporter()
        document_importer.gs = MagicMock(upload_file_from_string=mock_upload_file_from_string)

        download_url = document_importer.upload_file(upload_location, file_blob, file_type)

        mock_upload_file_from_string.assert_called_with(f'{upload_location}', file_blob, file_type)

        assert download_url == f'{settings.GC_PATH}location'

    def test_upload_file_fail_not_raise_exception(self):
        upload_location = 'location'
        file_blob = 'file_blob'
        file_type = 'file_type'

        mock_upload_file_from_string = MagicMock()
        mock_upload_file_from_string.side_effect = Exception()
        document_importer = DocumentImporter()
        document_importer.gs = MagicMock(upload_file_from_string=mock_upload_file_from_string)

        download_url = document_importer.upload_file(upload_location, file_blob, file_type)

        mock_upload_file_from_string.assert_called_with(upload_location, file_blob, file_type)

        assert download_url is None

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.document_importer.requests.get')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    @patch('data.services.document_importer.generate_from_blob', return_value='image_blob')
    def test_process_successfully(self, generate_from_blob_mock, get_mock):
        department_1 = DepartmentFactory(name='New Orleans PD')
        department_2 = DepartmentFactory(name='Baton Rouge PD')

        officer_1 = OfficerFactory(uid='officer-uid-1')
        officer_2 = OfficerFactory(uid='officer-uid-2')
        officer_3 = OfficerFactory(uid='officer-uid-3')

        old_document_1 = DocumentFactory(
            docid='00fa809e',
            hrg_no='1',
            matched_uid='officer-uid-1',
            agency='new-orleans-pd'
        )
        old_document_1.departments.add(department_1)
        old_document_1.officers.add(officer_1)
        old_document_1.save()

        old_document_2 = DocumentFactory(
            docid='0dd28391',
            hrg_no='1',
            matched_uid='officer-uid-3',
            agency='baton-rouge-pd'
        )
        old_document_2.departments.add(department_2)
        old_document_2.officers.add(officer_3)
        old_document_2.save()

        DocumentFactory(
            docid='0dd28391',
            hrg_no='3',
            matched_uid=None,
            pdf_db_content_hash='a3847e1c769816a9988f90fa02b77c9c9a239f48684b9ff2b6cbe134cb59a14c',
            url=f'{settings.GC_PATH}meeting-minutes-extraction/export/pdfs/0dd28391.pdf',
            preview_image_url=f'{settings.GC_PATH}meeting-minutes-extraction/export/pdfs/0dd28391-preview.jpeg',
        )

        assert Document.objects.count() == 3

        WrglRepoFactory(
            data_model=DocumentImporter.data_model,
            repo_name='document_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        commit_hash = '87d27e0616d9ef342e1728f5533162a3'

        document_importer = DocumentImporter()

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = commit_hash

        document_importer.repo = Mock()
        document_importer.new_commit = mock_commit

        document_importer.retrieve_wrgl_data = Mock()

        document_importer.old_column_mappings = {column: self.header.index(column) for column in self.header}
        document_importer.column_mappings = {column: self.header.index(column) for column in self.header}

        processed_data = {
            'added_rows': [
                self.document2_data,
                self.document4_data,
            ],
            'deleted_rows': [
                self.document3_data,
                self.document6_data,
            ],
            'updated_rows': [
                self.document1_data,
                self.document5_data,
            ],
        }

        document_importer.process_wrgl_data = Mock(return_value=processed_data)

        get_mock_return = Mock(headers={"content-type": 'application/pdf'})
        get_mock.return_value = get_mock_return

        def upload_file_side_effect(upload_location, _file_blob, _file_type):
            return f"{settings.GC_PATH}{upload_location}".replace(' ', '%20').replace("'", '%27')

        mock_upload_file = MagicMock(side_effect=upload_file_side_effect)
        document_importer.upload_file = mock_upload_file

        mock_get_temporary_link_from_path = Mock(return_value='https://example.com')
        document_importer.ds = Mock(get_temporary_link_from_path=mock_get_temporary_link_from_path)

        def get_ocr_text_side_effect(ocr_text_id):
            return f'ocr text for {ocr_text_id}'

        mock_get_ocr_text = Mock(side_effect=get_ocr_text_side_effect)
        document_importer.get_ocr_text = mock_get_ocr_text

        result = document_importer.process()

        assert result

        import_log = ImportLog.objects.order_by('-created_at').last()

        assert import_log.data_model == DocumentImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '87d27e0616d9ef342e1728f5533162a3'
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 2
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Document.objects.count() == 4

        check_columns = self.header + ['department_ids', 'officer_ids']
        check_columns_mappings = {column: check_columns.index(column) for column in check_columns}

        expected_document1_data = self.document1_data.copy()
        expected_document1_data.append([department_1.id])
        expected_document1_data.append([officer_1.id])

        expected_document2_data = self.document2_data.copy()
        expected_document2_data.append([])
        expected_document2_data.append([officer_2.id])

        expected_document3_data = self.document3_data.copy()
        expected_document3_data.append([department_2.id])
        expected_document3_data.append([officer_3.id])

        expected_document4_data = self.document4_data.copy()
        expected_document4_data.append([department_1.id])
        expected_document4_data.append([])

        expected_document5_data = self.document5_data.copy()
        expected_document5_data.append([])
        expected_document5_data.append([])

        expected_documents_data = [
            expected_document1_data,
            expected_document2_data,
            expected_document4_data,
            expected_document5_data,
        ]

        gs_upload_file_calls = []

        for document_data in expected_documents_data:
            document = Document.objects.filter(
                docid=document_data[check_columns_mappings['docid']] if document_data[
                    check_columns_mappings['docid']] else None,
                hrg_no=document_data[check_columns_mappings['hrg_no']] if document_data[
                    check_columns_mappings['hrg_no']] else None,
                matched_uid=document_data[check_columns_mappings['matched_uid']] if document_data[
                    check_columns_mappings['matched_uid']] else None,
                agency=slugify(document_data[check_columns_mappings['agency']]) if document_data[
                    check_columns_mappings['agency']] else None,
            ).first()
            assert document
            field_attrs = [
                'docid',
                'hrg_no',
                'matched_uid',
                'pdf_db_path',
                'pdf_db_content_hash',
                'txt_db_id',
                'txt_db_content_hash',
                'accused',
                'title'
            ]
            integer_field_attrs = [
                'year',
                'month',
                'day',
            ]

            for attr in field_attrs:
                assert getattr(document, attr) == (document_data[check_columns_mappings[attr]] if document_data[
                    check_columns_mappings[attr]] else None)

            for attr in integer_field_attrs:
                assert getattr(document, attr) == (int(document_data[check_columns_mappings[attr]]) if document_data[
                    check_columns_mappings[attr]] else None)

            base_url = document_data[check_columns_mappings['pdf_db_path']].replace('/PPACT/', '')
            document_url = f"{settings.GC_PATH}{base_url}".replace(' ', '%20').replace("'", '%27')

            upload_document_call = call(base_url, ANY, 'application/pdf')
            preview_image_dest = base_url.replace('.pdf', '-preview.jpeg').replace('.PDF', '-preview.jpeg')
            upload_document_preview_call = call(preview_image_dest, ANY, 'image/jpeg')
            gs_upload_file_calls.append(upload_document_call)
            gs_upload_file_calls.append(upload_document_preview_call)

            ocr_text = f'ocr text for {document_data[check_columns_mappings["txt_db_id"]]}'
            document_text_content = document_data[check_columns_mappings['hrg_text']] if document_data[
                check_columns_mappings['hrg_text']] else ocr_text

            assert document.text_content == document_text_content

            assert document.url == document_url
            assert document.preview_image_url == document_url.replace('.pdf', '-preview.jpeg').replace('.PDF',
                                                                                                       '-preview.jpeg')

            assert list(document.departments.values_list('id', flat=True)) == document_data[
                check_columns_mappings['department_ids']]
            assert list(document.officers.values_list('id', flat=True)) == document_data[
                check_columns_mappings['officer_ids']]

        assert mock_upload_file.call_count == 6

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.document_importer.requests.get')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    @patch('data.services.document_importer.generate_from_blob', return_value='image_blob')
    def test_process_successfully_with_columns_changed(self, generate_from_blob_mock, get_mock):
        department_1 = DepartmentFactory(name='New Orleans PD')
        department_2 = DepartmentFactory(name='Baton Rouge PD')

        officer_1 = OfficerFactory(uid='officer-uid-1')
        officer_2 = OfficerFactory(uid='officer-uid-2')
        officer_3 = OfficerFactory(uid='officer-uid-3')

        old_document_1 = DocumentFactory(
            docid='00fa809e',
            hrg_no='1',
            matched_uid='officer-uid-1',
            agency='new-orleans-pd'
        )
        old_document_1.departments.add(department_1)
        old_document_1.officers.add(officer_1)
        old_document_1.save()

        old_document_2 = DocumentFactory(
            docid='0dd28391',
            hrg_no='1',
            matched_uid='officer-uid-3',
            agency='baton-rouge-pd'
        )
        old_document_2.departments.add(department_2)
        old_document_2.officers.add(officer_3)
        old_document_2.save()

        DocumentFactory(
            docid='0dd28391',
            hrg_no='3',
            matched_uid=None,
            pdf_db_content_hash='a3847e1c769816a9988f90fa02b77c9c9a239f48684b9ff2b6cbe134cb59a14c',
            url=f'{settings.GC_PATH}meeting-minutes-extraction/export/pdfs/0dd28391.pdf',
            preview_image_url=f'{settings.GC_PATH}meeting-minutes-extraction/export/pdfs/0dd28391-preview.jpeg',
        )

        assert Document.objects.count() == 3

        WrglRepoFactory(
            data_model=DocumentImporter.data_model,
            repo_name='document_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        commit_hash = '87d27e0616d9ef342e1728f5533162a3'

        document_importer = DocumentImporter()

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = commit_hash

        document_importer.repo = Mock()
        document_importer.new_commit = mock_commit

        document_importer.retrieve_wrgl_data = Mock()

        old_columns = self.header[:-1]
        document_importer.old_column_mappings = {column: old_columns.index(column) for column in old_columns}
        document_importer.column_mappings = {column: self.header.index(column) for column in self.header}

        processed_data = {
            'added_rows': [
                self.document2_data,
                self.document4_data,
            ],
            'deleted_rows': [
                self.document3_data[:-1],
                self.document6_data[:-1],
            ],
            'updated_rows': [
                self.document1_data,
                self.document5_data,
            ],
        }

        document_importer.process_wrgl_data = Mock(return_value=processed_data)

        get_mock_return = Mock(headers={"content-type": 'application/pdf'})
        get_mock.return_value = get_mock_return

        def upload_file_side_effect(upload_location, _file_blob, _file_type):
            return f"{settings.GC_PATH}{upload_location}".replace(' ', '%20').replace("'", '%27')
        mock_upload_file = MagicMock(side_effect=upload_file_side_effect)
        document_importer.upload_file = mock_upload_file

        mock_get_temporary_link_from_path = Mock(return_value='https://example.com')
        document_importer.ds = Mock(get_temporary_link_from_path=mock_get_temporary_link_from_path)

        def get_ocr_text_side_effect(ocr_text_id):
            return f'ocr text for {ocr_text_id}'
        mock_get_ocr_text = Mock(side_effect=get_ocr_text_side_effect)
        document_importer.get_ocr_text = mock_get_ocr_text

        result = document_importer.process()

        assert result

        import_log = ImportLog.objects.order_by('-created_at').last()

        assert import_log.data_model == DocumentImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '87d27e0616d9ef342e1728f5533162a3'
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 2
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Document.objects.count() == 4

        check_columns = self.header + ['department_ids', 'officer_ids']
        check_columns_mappings = {column: check_columns.index(column) for column in check_columns}

        expected_document1_data = self.document1_data.copy()
        expected_document1_data.append([department_1.id])
        expected_document1_data.append([officer_1.id])

        expected_document2_data = self.document2_data.copy()
        expected_document2_data.append([])
        expected_document2_data.append([officer_2.id])

        expected_document3_data = self.document3_data.copy()
        expected_document3_data.append([department_2.id])
        expected_document3_data.append([officer_3.id])

        expected_document4_data = self.document4_data.copy()
        expected_document4_data.append([department_1.id])
        expected_document4_data.append([])

        expected_document5_data = self.document5_data.copy()
        expected_document5_data.append([])
        expected_document5_data.append([])

        expected_documents_data = [
            expected_document1_data,
            expected_document2_data,
            expected_document4_data,
            expected_document5_data,
        ]

        gs_upload_file_calls = []

        for document_data in expected_documents_data:
            document = Document.objects.filter(
                docid=document_data[check_columns_mappings['docid']] if document_data[
                    check_columns_mappings['docid']] else None,
                hrg_no=document_data[check_columns_mappings['hrg_no']] if document_data[
                    check_columns_mappings['hrg_no']] else None,
                matched_uid=document_data[check_columns_mappings['matched_uid']] if document_data[
                    check_columns_mappings['matched_uid']] else None,
                agency=slugify(document_data[check_columns_mappings['agency']]) if document_data[
                    check_columns_mappings['agency']] else None,
            ).first()
            assert document
            field_attrs = [
                'docid',
                'hrg_no',
                'matched_uid',
                'pdf_db_path',
                'pdf_db_content_hash',
                'txt_db_id',
                'txt_db_content_hash',
                'accused',
                'title'
            ]
            integer_field_attrs = [
                'year',
                'month',
                'day',
            ]

            for attr in field_attrs:
                assert getattr(document, attr) == (document_data[check_columns_mappings[attr]]
                                                   if document_data[check_columns_mappings[attr]] else None)

            for attr in integer_field_attrs:
                assert getattr(document, attr) == (int(document_data[check_columns_mappings[attr]])
                                                   if document_data[check_columns_mappings[attr]] else None)

            base_url = document_data[check_columns_mappings['pdf_db_path']].replace('/PPACT/', '')
            document_url = f"{settings.GC_PATH}{base_url}".replace(' ', '%20').replace("'", '%27')

            upload_document_call = call(base_url, ANY, 'application/pdf')
            preview_image_dest = base_url.replace('.pdf', '-preview.jpeg').replace('.PDF', '-preview.jpeg')
            upload_document_preview_call = call(preview_image_dest, ANY, 'image/jpeg')
            gs_upload_file_calls.append(upload_document_call)
            gs_upload_file_calls.append(upload_document_preview_call)

            ocr_text = f'ocr text for {document_data[check_columns_mappings["txt_db_id"]]}'
            document_text_content = document_data[check_columns_mappings['hrg_text']] if document_data[check_columns_mappings['hrg_text']] else ocr_text

            assert document.text_content == document_text_content

            assert document.url == document_url
            assert document.preview_image_url == document_url.replace('.pdf', '-preview.jpeg').replace('.PDF', '-preview.jpeg')

            assert list(document.departments.values_list('id', flat=True)) == document_data[check_columns_mappings['department_ids']]
            assert list(document.officers.values_list('id', flat=True)) == document_data[check_columns_mappings['officer_ids']]

        assert mock_upload_file.call_count == 6

    @patch('data.services.document_importer.generate_from_blob', return_value='preview_image_blob')
    def test_generate_preview_image_success(self, _):
        image_blob = 'image_blob'
        upload_url = 'path/to/file.pdf'

        mock_upload_file_from_string = MagicMock()
        document_importer = DocumentImporter()
        document_importer.gs = MagicMock(upload_file_from_string=mock_upload_file_from_string)

        preview_image_url = document_importer.generate_preview_image(image_blob, upload_url)

        mock_upload_file_from_string.assert_called_with(
            'path/to/file-preview.jpeg',
            'preview_image_blob',
            'image/jpeg'
        )
        assert preview_image_url == f'{settings.GC_PATH}path/to/file-preview.jpeg'

    @patch('data.services.document_importer.generate_from_blob', return_value=None)
    def test_generate_preview_image_fail(self, _):
        image_blob = 'image_blob'
        upload_url = 'path/to/file.pdf'

        mock_upload_file_from_string = MagicMock()
        document_importer = DocumentImporter()
        document_importer.gs = MagicMock(upload_file_from_string=mock_upload_file_from_string)

        preview_image_url = document_importer.generate_preview_image(image_blob, upload_url)

        mock_upload_file_from_string.assert_not_called()
        assert preview_image_url is None

    @patch('data.services.document_importer.requests.get')
    def test_get_ocr_text_success(self, get_mock):
        get_mock_return = Mock(text='decoded_value')
        get_mock.return_value = get_mock_return

        mock_get_temporary_link_from_path = Mock(return_value='temp_link')
        mock_dropbox = Mock(get_temporary_link_from_path=mock_get_temporary_link_from_path)

        document_importer = DocumentImporter()
        document_importer.ds = mock_dropbox

        ocr_text_id = 'ocr_text_id'
        ocr_text = document_importer.get_ocr_text(ocr_text_id)

        mock_get_temporary_link_from_path.assert_called_with(ocr_text_id)
        get_mock.assert_called_with('temp_link')
        assert ocr_text == 'decoded_value'

    @patch('data.services.document_importer.requests.get')
    def test_get_ocr_text_fail(self, get_mock):
        mock_get_temporary_link_from_path = Mock()
        mock_get_temporary_link_from_path.side_effect = Exception()
        mock_dropbox = Mock(get_temporary_link_from_path=mock_get_temporary_link_from_path)

        document_importer = DocumentImporter()
        document_importer.ds = mock_dropbox

        ocr_text_id = 'ocr_text_id'
        ocr_text = document_importer.get_ocr_text(ocr_text_id)

        assert ocr_text == ''

    @patch('data.services.document_importer.requests.get')
    def test_handle_pdf_file_process_success(self, get_mock):
        get_mock_return = Mock(headers={"content-type": 'application/pdf'})
        get_mock.return_value = get_mock_return

        mock_get_temporary_link_from_path = Mock(return_value='temp_link')
        mock_dropbox = Mock(get_temporary_link_from_path=mock_get_temporary_link_from_path)

        document_importer = DocumentImporter()
        document_importer.ds = mock_dropbox
        document_importer.generate_preview_image = Mock(return_value='preview_image_blob')

        pdf_db_path = 'pdf_db_path'
        uploaded_url = document_importer.handle_file_process(pdf_db_path)

        mock_get_temporary_link_from_path.assert_called_with(pdf_db_path)
        get_mock.assert_called_with('temp_link')
        assert uploaded_url == {
            'document_url': 'https://storage.googleapis.com/llead-documents-test/pdf_db_path',
            'document_preview_url': 'preview_image_blob',
            'document_type': 'application/pdf',
        }

    @patch('data.services.document_importer.requests.get')
    def test_handle_doc_file_process_success(self, get_mock):
        get_mock_return = Mock(headers={"content-type": 'application/msword'})
        get_mock.return_value = get_mock_return

        mock_get_temporary_link_from_path = Mock(return_value='temp_link')
        mock_dropbox = Mock(get_temporary_link_from_path=mock_get_temporary_link_from_path)

        document_importer = DocumentImporter()
        document_importer.ds = mock_dropbox
        document_importer.generate_preview_image = Mock(return_value='preview_image_blob')

        pdf_db_path = 'pdf_db_path'
        uploaded_url = document_importer.handle_file_process(pdf_db_path)

        mock_get_temporary_link_from_path.assert_called_with(pdf_db_path)
        get_mock.assert_called_with('temp_link')
        assert uploaded_url == {
            'document_url': 'https://storage.googleapis.com/llead-documents-test/pdf_db_path',
            'document_preview_url': None,
            'document_type': 'application/msword',
        }

    @patch('data.services.document_importer.requests.get')
    @override_settings(GC_PATH='')
    def test_handle_file_process_fail(self, get_mock):
        get_mock_return = Mock(headers={"content-type": 'application/pdf'})
        get_mock.return_value = get_mock_return

        mock_get_temporary_link_from_path = Mock(return_value='temp_link')
        mock_dropbox = Mock(get_temporary_link_from_path=mock_get_temporary_link_from_path)

        document_importer = DocumentImporter()
        document_importer.ds = mock_dropbox
        document_importer.generate_preview_image = Mock(return_value='preview_image_blob')

        pdf_db_path = ''
        uploaded_url = document_importer.handle_file_process(pdf_db_path)

        mock_get_temporary_link_from_path.assert_called_with(pdf_db_path)
        get_mock.assert_called_with('temp_link')
        assert uploaded_url == {}
