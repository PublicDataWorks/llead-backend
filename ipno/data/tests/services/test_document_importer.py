import json
from inspect import cleandoc
from io import StringIO, BytesIO
from csv import DictWriter

from unittest.mock import call, ANY
from django.test.testcases import TestCase, override_settings
from mock import patch, Mock, MagicMock

from dropbox.exceptions import ApiError

from data.services import DocumentImporter
from data.models import ImportLog
from data.constants import IMPORT_LOG_STATUS_FINISHED, GC_PATH, IMPORT_LOG_STATUS_ERROR
from data.factories import WrglRepoFactory
from documents.models import Document
from documents.factories import DocumentFactory
from officers.factories import OfficerFactory
from departments.factories import DepartmentFactory


class DocumentImporterTestCase(TestCase):
    def setUp(self):
        self.patcher = patch('data.services.document_importer.GoogleCloudService')
        self.patcher.start()

        csv_content = StringIO()
        writer = DictWriter(
            csv_content,
            fieldnames=[
                'docid',
                'page_count',
                'fileid',
                'file_db_path',
                'file_db_id',
                'file_db_content_hash',
                'year',
                'month',
                'day',
                'dt_source',
                'hrg_no',
                'accused',
                'matched_uid',
                'hrg_text',
                'ocr_text',
                'agency'
            ]
        )
        self.document1_data = {
            'docid': '00fa809e',
            'page_count': '4',
            'fileid': 'f0fcc0d',
            'file_db_path': '/PPACT/meeting-minutes-extraction/export/pdfs/00fa809e.pdf',
            'file_db_id': 'id:8ceKnrnmgi0AAAAAAAAqmQ',
            'file_db_content_hash': 'ceb9779f43154497099356c8bd74cacce1faa780cb6916a85efc8b4e278a776c',
            'year': '2018',
            'month': '6',
            'day': '14',
            'dt_source': 'scraped',
            'hrg_no': '1',
            'accused': 'Joseph Jones, Docket No. 17-',
            'matched_uid': 'officer-uid-1',
            'agency': 'New Orleans PD',
            'hrg_text': cleandoc("""
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
            'ocr_text': cleandoc("""
                Action/Minutes
                AGENDA
                John Bel Edwards
                LOUISIANA STATE POLICE COMMISSION Governor
                GENERAL BUSINESS MEETING
                THURSDAY. JUNE 14, 2018 Jason Hannaman
                9:00 A.M. Executive Director
                STATE POLICE COMMISSION, VETERANS MEMORIAL AUDITORIUM, SUITE 1247,
                DEPT. OF AGRICULTURE & FORESTRY BLDG., 5825 FLORIDA BLVD., BATON ROUGE, LA 70806
                I. Call to Order
                The State Police Commission convened its monthly general business meeting at 9:09 A.M.
                on Thursday, June 14, 2018.
            """)
        }
        self.document2_data = {
            'docid': '0236e725',
            'page_count': '1',
            'fileid': 'd4fb65b',
            'file_db_path': '/PPACT/meeting-minutes-extraction/export/pdfs/0236e725.pdf',
            'file_db_id': 'id:8ceKnrnmgi0AAAAAAAAqmw',
            'file_db_content_hash': '5f05f28383649aad924c89627c864c615856974d22f2eb53a6bdcf4464c76d20',
            'year': '2018',
            'month': '12',
            'day': '18',
            'dt_source': 'scraped',
            'hrg_no': '1',
            'accused': 'Officer Terry Guillory, Docket 17-201',
            'matched_uid': 'officer-uid-2',
            'agency': '',
            'hrg_text': cleandoc("""
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
            'ocr_text': cleandoc("""
                Municipal Police Employees Civil Service Board
                MINUTES OF MUNICIPAL POLICE EMPLOYEES’ MEETING
                DATE: Tuesday, December 18, 2018
                TIME: 5:07PM
                LOCATION: Mandeville City Hall Courtroom
                3101 East Causeway Approach
                Mandeville, LA 70448
                ATTENDANCE:
                Brian Burke, Chairman Present
                Roxanne Luquet, Vice-Chairman Present
                Jack McGuire Present
                Richard Ainsworth Absent
                Dr. Dennis Mutell Absent
            """)
        }
        self.document3_data = {
            'docid': '0dd28391',
            'page_count': '3',
            'fileid': '77d489c',
            'file_db_path': '/PPACT/meeting-minutes-extraction/export/pdfs/0dd28391.pdf',
            'file_db_id': 'id:8ceKnrnmgi0AAAAAAAAqng',
            'file_db_content_hash': 'a3847e1c769816a9988f90fa02b77c9c9a239f48684b9ff2b6cbe134cb59a14c',
            'year': '1999',
            'month': '9',
            'day': '30',
            'dt_source': 'scraped',
            'hrg_no': '1',
            'accused': 'WILLIAM C. BROWN',
            'matched_uid': 'officer-uid-3',
            'agency': 'Baton Rouge PD',
            'hrg_text': cleandoc("""
                APPEAL HEARING FOR WILLIAM C. BROWN
                Mr. William C. Brown submitted a request to withdraw his appeal. A motion was made by
                Henry Clark to accept this request for withdrawal and seconded by Lyle Johnson. Motion
                approved unanimously.
            """),
            'ocr_text': cleandoc("""
                — APPROVED
                MUNICIPAL FIRE AND POLICE CIVIL SERVICE BOARD
                THURSDAY, SEPTEMBER 30, 1999 @ 9:30 A.M.
                METROPOLITAN COUNCIL CHAMBERS
                3RD FLOOR - GOVERNMENTAL BUILDING
                BATON ROUGE, LOUISIANA
                ROLL CALL
                Johnny Johnston, Chairman
                Henry Clark, Vice Chairman
                Dary! Edgens
                Lyle Johnson
                Cynthia Wilkinson
                David Hamilton, Attorney
                Margaret Johnson, Secretary to Board
                APPROVE MINUTES
            """)
        }
        self.document4_data = {
            'docid': '0dd28391',
            'page_count': '3',
            'fileid': '77d489c',
            'file_db_path': '/PPACT/meeting-minutes-extraction/export/pdfs/0dd28391.pdf',
            'file_db_id': 'id:8ceKnrnmgi0AAAAAAAAqng',
            'file_db_content_hash': 'a3847e1c769816a9988f90fa02b77c9c9a239f48684b9ff2b6cbe134cb59a14c',
            'year': '1999',
            'month': '9',
            'day': '30',
            'dt_source': 'scraped',
            'hrg_no': '2',
            'accused': 'JIM VERLANDER',
            'matched_uid': 'officer-uid-invalid',
            'agency': 'New Orleans PD',
            'hrg_text': cleandoc("""
                APPEAL HEARING FOR JIM VERLANDER
                Mr. Verlander has submitted a letter stating that an agreement has been reached between
                himself and Chief Phares. Board asks that Ms. Johnson make sure that a Personnel Action
                form is received from Chief Phares regarding the agreement.
                Cynthia Wilkinson made a motion to accept the letter tentatively until a Personnel Action
                form is received from Chief Phares regarding the agreement. This motion was seconded by
                Lyle Johnson. Motion approved unanimously.
            """),
            'ocr_text': cleandoc("""
                — APPROVED
                MUNICIPAL FIRE AND POLICE CIVIL SERVICE BOARD
                THURSDAY, SEPTEMBER 30, 1999 @ 9:30 A.M.
                METROPOLITAN COUNCIL CHAMBERS
                3RD FLOOR - GOVERNMENTAL BUILDING
                BATON ROUGE, LOUISIANA
                ROLL CALL
                Johnny Johnston, Chairman
                Henry Clark, Vice Chairman
                Dary! Edgens
                Lyle Johnson
                Cynthia Wilkinson
                David Hamilton, Attorney
                Margaret Johnson, Secretary to Board
                APPROVE MINUTES
            """)
        }
        self.document5_data = {
            'docid': '0dd28391',
            'page_count': '3',
            'fileid': '77d489c',
            'file_db_path': '/PPACT/meeting-minutes-extraction/export/pdfs/0dd28391.pdf',
            'file_db_id': 'id:8ceKnrnmgi0AAAAAAAAqng',
            'file_db_content_hash': 'a3847e1c769816a9988f90fa02b77c9c9a239f48684b9ff2b6cbe134cb59a14c',
            'year': '1999',
            'month': '9',
            'day': '30',
            'dt_source': 'scraped',
            'hrg_no': '3',
            'accused': 'OFFICER KEVIN LAPEYROUSE',
            'matched_uid': 'NA',
            'agency': '',
            'hrg_text': cleandoc("""
                APPEAL HEARING FOR OFFICER KEVIN LAPEYROUSE
                Kevin Lapeyrouse did not appear for this hearing, therefore Henry Clark made a motion to
                not hear this appeal due to the appellant not appearing or contacting anyone in regard to this
                hearing and Cynthia Wilkinson seconded this motion. Motion approved unanimously.
                Ma.
            """),
            'ocr_text': cleandoc("""
                — APPROVED
                MUNICIPAL FIRE AND POLICE CIVIL SERVICE BOARD
                THURSDAY, SEPTEMBER 30, 1999 @ 9:30 A.M.
                METROPOLITAN COUNCIL CHAMBERS
                3RD FLOOR - GOVERNMENTAL BUILDING
                BATON ROUGE, LOUISIANA
                ROLL CALL
                Johnny Johnston, Chairman
                Henry Clark, Vice Chairman
                Dary! Edgens
                Lyle Johnson
                Cynthia Wilkinson
                David Hamilton, Attorney
                Margaret Johnson, Secretary to Board
                APPROVE MINUTES
            """)
        }
        self.documents_data = [
            self.document1_data,
            self.document2_data,
            self.document3_data,
            self.document4_data,
            self.document5_data,
            self.document5_data,
        ]
        writer.writeheader()
        writer.writerows(self.documents_data)
        self.csv_stream = BytesIO(csv_content.getvalue().encode('utf-8'))

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    @patch('data.services.document_importer.generate_from_blob', return_value='image_blob')
    @patch('urllib.request.urlopen')
    def test_process_successfully(self, urlopen_mock, generate_from_blob_mock):
        DocumentFactory(docid='00fa809e', hrg_no='1', matched_uid='officer-uid-1')
        DocumentFactory(docid='00fa809e', hrg_no='10', matched_uid=None)
        DocumentFactory(
            docid='0dd28391',
            hrg_no='3',
            matched_uid=None,
            file_db_content_hash='a3847e1c769816a9988f90fa02b77c9c9a239f48684b9ff2b6cbe134cb59a14c',
            url='https://storage.googleapis.com/llead-documents/meeting-minutes-extraction/export/pdfs/0dd28391.pdf',
            preview_image_url='https://storage.googleapis.com/llead-documents/meeting-minutes-extraction/export/pdfs/0dd28391-preview.jpeg',
        )

        department_1 = DepartmentFactory(name='New Orleans PD')
        department_2 = DepartmentFactory(name='Baton Rouge PD')

        officer_1 = OfficerFactory(uid='officer-uid-1')
        officer_2 = OfficerFactory(uid='officer-uid-2')
        officer_3 = OfficerFactory(uid='officer-uid-3')

        assert Document.objects.count() == 3

        WrglRepoFactory(
            data_model=DocumentImporter.data_model,
            repo_name='document_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        data = {
            'hash': '87d27e0616d9ef342e1728f5533162a3'
        }
        repo_details_stream = BytesIO(json.dumps(data).encode('utf-8'))
        urlopen_mock.side_effect = [repo_details_stream, self.csv_stream, 'file_blob']

        document_importer = DocumentImporter()

        def upload_file_side_effect(upload_location, _file_blob, _file_type):
            return f"{GC_PATH}{upload_location}".replace(' ', '%20').replace("'", '%27')
        mock_upload_file = MagicMock(side_effect=upload_file_side_effect)
        mock_clean_up_document = MagicMock()
        document_importer.upload_file = mock_upload_file
        document_importer.clean_up_document = mock_clean_up_document

        mock_get_temporary_link_from_path = Mock(return_value='https://example.com')
        document_importer.ds = Mock(get_temporary_link_from_path=mock_get_temporary_link_from_path)
        document_importer.process()

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == DocumentImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '87d27e0616d9ef342e1728f5533162a3'
        assert import_log.created_rows == 3
        assert import_log.updated_rows == 3
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Document.objects.count() == 5

        repo_details_request = urlopen_mock.call_args_list[0][0][0]
        assert repo_details_request._full_url == 'https://www.wrgl.co/api/v1/users/wrgl_user/repos/document_repo'
        assert repo_details_request.headers == {
            'Authorization': 'APIKEY wrgl-api-key'
        }

        expected_document1_data = self.document1_data.copy()
        expected_document1_data['department_ids'] = [department_1.id]
        expected_document1_data['officer_ids'] = [officer_1.id]

        expected_document2_data = self.document2_data.copy()
        expected_document2_data['department_ids'] = []
        expected_document2_data['officer_ids'] = [officer_2.id]

        expected_document3_data = self.document3_data.copy()
        expected_document3_data['department_ids'] = [department_2.id]
        expected_document3_data['officer_ids'] = [officer_3.id]

        expected_document4_data = self.document4_data.copy()
        expected_document4_data['department_ids'] = [department_1.id]
        expected_document4_data['officer_ids'] = []

        expected_document5_data = self.document5_data.copy()
        expected_document5_data['department_ids'] = []
        expected_document5_data['officer_ids'] = []

        expected_documents_data = [
            expected_document1_data,
            expected_document2_data,
            expected_document3_data,
            expected_document4_data,
            expected_document5_data,
        ]

        gs_upload_file_calls = []

        for document_data in expected_documents_data:
            document = Document.objects.filter(
                docid=document_data['docid'] if document_data['docid'] else None,
                hrg_no=document_data['hrg_no'] if document_data['hrg_no'] else None,
                matched_uid=document_data['matched_uid'] if document_data['matched_uid'] != 'NA' else None,
            ).first()
            assert document
            field_attrs = [
                'docid',
                'hrg_no',
                'fileid',
                'file_db_path',
                'file_db_content_hash',
                'accused',
            ]
            integer_field_attrs = [
                'year',
                'month',
                'day',
            ]

            for attr in field_attrs:
                assert getattr(document, attr) == (document_data[attr] if document_data[attr] else None)

            for attr in integer_field_attrs:
                assert getattr(document, attr) == (int(document_data[attr]) if document_data[attr] else None)

            base_url = document_data['file_db_path'].replace('/PPACT/', '')
            document_url = f"{GC_PATH}{base_url}".replace(' ', '%20').replace("'", '%27')

            upload_document_call = call(base_url, ANY, 'application/pdf')
            preview_image_dest = base_url.replace('.pdf', '-preview.jpeg').replace('.PDF', '-preview.jpeg')
            upload_document_preview_call = call(preview_image_dest, ANY, 'image/jpeg')
            gs_upload_file_calls.append(upload_document_call)
            gs_upload_file_calls.append(upload_document_preview_call)

            assert document.url == document_url
            assert document.preview_image_url == document_url.replace('.pdf', '-preview.jpeg').replace('.PDF', '-preview.jpeg')
            assert document.title == document_data['file_db_path'].split('/')[-1].replace('.pdf', '').replace('_', ' ')

            assert list(document.departments.values_list('id', flat=True)) == document_data['department_ids']
            assert list(document.officers.values_list('id', flat=True)) == document_data['officer_ids']

        assert mock_upload_file.call_count == 6
        assert mock_clean_up_document.call_count == 2

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    @patch('urllib.request.urlopen')
    def test_process_fail_dueto_dropbox_get_file_error(self, urlopen_mock):
        WrglRepoFactory(
            data_model=DocumentImporter.data_model,
            repo_name='document_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        data = {
            'hash': '87d27e0616d9ef342e1728f5533162a3'
        }
        repo_details_stream = BytesIO(json.dumps(data).encode('utf-8'))
        urlopen_mock.side_effect = [repo_details_stream, self.csv_stream, 'file_blob']

        document_importer = DocumentImporter()

        def upload_file_side_effect(upload_location, _file_blob, _file_type):
            return f"{GC_PATH}{upload_location}".replace(' ', '%20').replace("'", '%27')

        mock_upload_file = MagicMock(side_effect=upload_file_side_effect)
        mock_clean_up_document = MagicMock()
        document_importer.upload_file = mock_upload_file
        document_importer.clean_up_document = mock_clean_up_document

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

    def test_clean_up_document_success(self):
        doc = {
            'url': 'https://storage.googleapis.com/llead-documents/00fa809e.pdf',
            'preview_image_url': 'https://storage.googleapis.com/llead-documents/00fa809e-preview.img'
        }

        mock_delete_file_from_url = MagicMock()
        document_importer = DocumentImporter()
        document_importer.gs = MagicMock(delete_file_from_url=mock_delete_file_from_url)

        document_importer.clean_up_document(doc)

        mock_delete_file_from_url.assert_has_calls([
            call('00fa809e.pdf'),
            call('00fa809e-preview.img'),
        ])

    def test_clean_up_empty_document(self):
        doc = {}

        mock_delete_file_from_url = MagicMock()
        document_importer = DocumentImporter()
        document_importer.gs = MagicMock(delete_file_from_url=mock_delete_file_from_url)

        document_importer.clean_up_document(doc)

        mock_delete_file_from_url.assert_not_called()

    def test_clean_up_document_success_event_delete_raise_exception(self):
        doc = {
            'url': 'https://storage.googleapis.com/llead-documents/00fa809e.pdf',
            'preview_image_url': 'https://storage.googleapis.com/llead-documents/00fa809e-preview.img'
        }

        mock_delete_file_from_url = MagicMock()
        mock_delete_file_from_url.side_effect = [Exception(), Exception()]
        document_importer = DocumentImporter()
        document_importer.gs = MagicMock(delete_file_from_url=mock_delete_file_from_url)

        document_importer.clean_up_document(doc)

        mock_delete_file_from_url.assert_has_calls([
            call('00fa809e.pdf'),
            call('00fa809e-preview.img'),
        ])

    def test_clean_up_documents(self):
        doc1 = {
            'url': 'https://storage.googleapis.com/llead-documents/00fa809e.pdf',
            'preview_image_url': 'https://storage.googleapis.com/llead-documents/00fa809e-preview.img'
        }
        doc2 = {
            'url': 'https://storage.googleapis.com/llead-documents/abc/doc2.pdf',
            'preview_image_url': 'https://storage.googleapis.com/llead-documents/abc/doc2-preview.img'
        }
        documents = [doc1, doc2]

        mock_delete_file_from_url = MagicMock()
        document_importer = DocumentImporter()
        document_importer.gs = MagicMock(delete_file_from_url=mock_delete_file_from_url)

        document_importer.clean_up_documents(documents)

        mock_delete_file_from_url.assert_has_calls([
            call('00fa809e.pdf'),
            call('00fa809e-preview.img'),
            call('abc/doc2.pdf'),
            call('abc/doc2-preview.img')
        ])

    def test_upload_file_success(self):
        upload_location = 'location'
        file_blob = 'file_blob'
        file_type = 'file_type'

        mock_upload_file_from_string = MagicMock()
        document_importer = DocumentImporter()
        document_importer.gs = MagicMock(upload_file_from_string=mock_upload_file_from_string)

        download_url = document_importer.upload_file(upload_location, file_blob, file_type)

        mock_upload_file_from_string.assert_called_with(upload_location, file_blob, file_type)

        assert download_url == 'https://storage.googleapis.com/llead-documents/location'

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
        assert preview_image_url == 'https://storage.googleapis.com/llead-documents/path/to/file-preview.jpeg'

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
