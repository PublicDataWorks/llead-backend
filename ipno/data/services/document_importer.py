from itertools import chain

from django.template.defaultfilters import slugify
from django.conf import settings
from tqdm import tqdm
import requests
from dropbox.exceptions import ApiError

from documents.models import Document
from data.services.base_importer import BaseImporter
from data.constants import DOCUMENT_MODEL_NAME
from utils.parse_utils import parse_date
from utils.image_generator import generate_from_blob
from utils.google_cloud import GoogleCloudService
from utils.dropbox_utils import DropboxService


BATCH_SIZE = 1000


class DocumentImporter(BaseImporter):
    data_model = DOCUMENT_MODEL_NAME
    ATTRIBUTES = [
        'docid',
        'hrg_no',
        'matched_uid',
        'pdf_db_path',
        'pdf_db_content_hash',
        'txt_db_id',
        'txt_db_content_hash',
        'accused',
        'title',
        'hrg_type',
    ]
    INT_ATTRIBUTES = [
        'year',
        'month',
        'day',
    ]
    UPDATE_ATTRIBUTES = ATTRIBUTES + INT_ATTRIBUTES + [
        'document_type',
        'url',
        'preview_image_url',
        'incident_date',
        'text_content',
        'pages_count',
    ]

    def __init__(self):
        self.gs = GoogleCloudService()
        self.ds = DropboxService()

        self.new_documents = []
        self.update_documents = []
        self.new_docids = []
        self.delete_documents_ids = []
        self.document_mappings = {}
        self.uploaded_files = {}

    def get_document_mappings(self):
        documents_attrs = [
            'id', 'docid', 'hrg_no', 'matched_uid', 'pdf_db_content_hash', 'url', 'preview_image_url',
            'txt_db_content_hash'
        ]
        documents = Document.objects.values(*documents_attrs)
        return {
            (document['docid'], document['hrg_no'], document['matched_uid']): document for document in documents
        }

    def update_relations(self, raw_data):
        DepartmentRelation = Document.departments.through
        OfficerRelation = Document.officers.through
        department_relation_ids = {}
        officer_relation_ids = {}
        modified_documents_ids = []

        saved_data = list(chain(
            raw_data.get('added_rows', []),
            raw_data.get('updated_rows', []),
        ))
        deleted_data = raw_data.get('deleted_rows', [])

        officer_mappings = self.get_officer_mappings()
        agencies = {
            row[self.column_mappings['agency']] for row in saved_data if row[self.column_mappings['agency']]
        }
        agencies.update([
            row[self.old_column_mappings['agency']] for row in deleted_data if row[self.old_column_mappings['agency']]
        ])

        department_mappings = self.get_department_mappings(agencies)

        document_mappings = self.get_document_mappings()

        for row in tqdm(saved_data, desc="Update saved documents' relations"):
            document_data = self.parse_row_data(row, self.column_mappings)
            officer_uid = document_data.get('matched_uid')
            agency = row[self.column_mappings['agency']]

            if officer_uid or agency:
                docid = document_data['docid']
                hrg_no = document_data['hrg_no']
                matched_uid = officer_uid

                document = document_mappings.get((docid, hrg_no, matched_uid))
                document_id = document.get('id') if document else None

                if document_id:
                    modified_documents_ids.append(document_id)

                    if officer_uid:
                        officer_id = officer_mappings.get(officer_uid)
                        if officer_id:
                            officer_relation_ids[document_id] = officer_id

                    if agency:
                        formatted_agency = self.format_agency(agency)
                        department_id = department_mappings.get(slugify(formatted_agency))
                        if department_id:
                            department_relation_ids[document_id] = department_id

        for row in tqdm(deleted_data, desc="Update deleted documents' relations"):
            document_data = self.parse_row_data(row, self.old_column_mappings)
            officer_uid = document_data.get('matched_uid')
            agency = row[self.old_column_mappings['agency']]

            if officer_uid or agency:
                docid = document_data['docid']
                hrg_no = document_data['hrg_no']
                matched_uid = officer_uid

                document = document_mappings.get((docid, hrg_no, matched_uid))
                document_id = document.get('id') if document else None

                if document_id:
                    modified_documents_ids.append(document_id)

        department_relations = [
            DepartmentRelation(document_id=document_id, department_id=department_id)
            for document_id, department_id in department_relation_ids.items()
        ]

        officer_relations = [
            OfficerRelation(document_id=document_id, officer_id=officer_id)
            for document_id, officer_id in officer_relation_ids.items()
        ]

        DepartmentRelation.objects.filter(document_id__in=modified_documents_ids).delete()
        DepartmentRelation.objects.bulk_create(department_relations, batch_size=self.BATCH_SIZE)

        OfficerRelation.objects.filter(document_id__in=modified_documents_ids).delete()
        OfficerRelation.objects.bulk_create(officer_relations, batch_size=BATCH_SIZE)

    def generate_preview_image(self, image_blob, upload_url):
        preview_url_location = upload_url.replace('.pdf', '-preview.jpeg').replace('.PDF', '-preview.jpeg')
        preview_image_blob = generate_from_blob(image_blob)

        if preview_image_blob:
            return self.upload_file(preview_url_location, preview_image_blob, 'image/jpeg')

    def upload_file(self, upload_location, file_blob, file_type):
        try:
            self.gs.upload_file_from_string(upload_location, file_blob, file_type)

            download_url = f"{settings.GC_PATH}{upload_location}".replace(' ', '%20').replace("'", '%27')

            return download_url
        except Exception:
            pass

    def get_ocr_text(self, ocr_text_id):
        try:
            download_url = self.ds.get_temporary_link_from_path(ocr_text_id)
            text = requests.get(download_url).text
            return text
        except Exception:
            return ''

    def clean_up_document(self, document):
        document_url = document.get('url')
        document_preview_url = document.get('preview_image_url')

        if document_url:
            try:
                self.gs.delete_file_from_url(document_url.replace(settings.GC_PATH, ''))
            except Exception:
                pass

        if document_preview_url:
            try:
                self.gs.delete_file_from_url(document_preview_url.replace(settings.GC_PATH, ''))
            except Exception:
                pass

    def clean_up_documents(self, documents):
        for document in documents:
            self.clean_up_document(document)

    def handle_record_data(self, row):
        document_data = self.parse_row_data(row, self.column_mappings)
        document_data['document_type'] = 'pdf'
        document_data['pages_count'] = row[self.column_mappings['page_count']] if row[
            self.column_mappings['page_count']] else None
        document_data['incident_date'] = parse_date(
            document_data['year'],
            document_data['month'],
            document_data['day']
        )
        pdf_db_path = document_data['pdf_db_path']

        should_upload_file = False

        docid = document_data.get('docid')
        hrg_no = document_data.get('hrg_no')
        matched_uid = document_data.get('matched_uid')

        old_document = self.document_mappings.get((docid, hrg_no, matched_uid))

        document = {
            **(old_document or {}),
            **document_data
        }

        if old_document:
            if document_data['pdf_db_content_hash'] != old_document.get('pdf_db_content_hash'):
                should_upload_file = True
                self.clean_up_document(old_document)
        elif (docid, hrg_no, matched_uid) not in self.new_docids:
            should_upload_file = True

        if should_upload_file:
            try:
                if pdf_db_path in self.uploaded_files:
                    uploaded_file = self.uploaded_files[pdf_db_path]
                    document['url'] = uploaded_file['document_url']
                    document['preview_image_url'] = uploaded_file['document_preview_url']
                else:
                    upload_url = pdf_db_path.replace('/PPACT/', '')

                    download_url = self.ds.get_temporary_link_from_path(pdf_db_path.replace('/PPACT/', '/LLEAD/'))
                    image_blob = requests.get(download_url).content

                    document_url = self.upload_file(upload_url, image_blob, 'application/pdf')

                    if not document_url:
                        return
                    document['url'] = document_url

                    document_preview_url = self.generate_preview_image(image_blob, upload_url)
                    if document_preview_url:
                        document['preview_image_url'] = document_preview_url

                    uploaded_url = {
                        'document_url': document_url,
                        'document_preview_url': document_preview_url
                    }

                    self.uploaded_files[pdf_db_path] = uploaded_url
            except ApiError:
                raise ValueError(f'Error downloading dropbox file from path: {pdf_db_path}')

        hrg_text = row[self.column_mappings['hrg_text']]
        if hrg_text:
            document['text_content'] = hrg_text
        else:
            old_txt_db_content_hash = old_document.get('txt_db_content_hash') if old_document else None
            if document_data['txt_db_content_hash'] != old_txt_db_content_hash:
                ocr_text = self.get_ocr_text(document_data['txt_db_id'].replace('/PPACT/', '/LLEAD/'))
                document['text_content'] = ocr_text

        if document:
            if old_document:
                self.update_documents.append(document)
            elif (docid, hrg_no, matched_uid) not in self.new_docids:
                self.new_docids.append((docid, hrg_no, matched_uid))
                self.new_documents.append(document)

    def import_data(self, data):
        self.document_mappings = self.get_document_mappings()

        for row in tqdm(data.get('added_rows'), desc='Create new documents'):
            self.handle_record_data(row)

        for row in tqdm(data.get('deleted_rows'), desc='Delete removed documents'):
            document_data = self.parse_row_data(row, self.old_column_mappings)
            docid = document_data.get('docid')
            hrg_no = document_data.get('hrg_no')
            matched_uid = document_data.get('matched_uid')

            old_document = self.document_mappings.get((docid, hrg_no, matched_uid))

            if old_document:
                self.delete_documents_ids.append(old_document.get('id'))

        for row in tqdm(data.get('updated_rows'), desc='Update modified documents'):
            self.handle_record_data(row)

        import_result = self.bulk_import(
            Document,
            self.new_documents,
            self.update_documents,
            self.delete_documents_ids,
            self.clean_up_documents
        )

        self.update_relations(data)

        return import_result
