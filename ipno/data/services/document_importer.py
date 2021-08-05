from tqdm import tqdm
from urllib.request import urlopen
from dropbox.exceptions import ApiError

from documents.models import Document
from data.services.base_importer import BaseImporter
from data.constants import DOCUMENT_MODEL_NAME, GC_PATH
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
        'title'
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

    def document_mappings(self):
        documents_attrs = [
            'id', 'docid', 'hrg_no', 'matched_uid', 'pdf_db_content_hash', 'url', 'preview_image_url',
            'txt_db_content_hash'
        ]
        documents = Document.objects.values(*documents_attrs)
        return {
            (document['docid'], document['hrg_no'], document['matched_uid']): document for document in documents
        }

    def update_relations(self, data):
        DepartmentRelation = Document.departments.through
        OfficerRelation = Document.officers.through
        department_relation_ids = {}
        officer_relation_ids = {}

        officer_mappings = self.officer_mappings()
        agencies = {row['agency'] for row in data if row['agency']}
        department_mappings = self.department_mappings(agencies)

        document_mappings = self.document_mappings()

        for row in tqdm(data):
            officer_uid = row['matched_uid'] if row['matched_uid'] else None
            agency = row['agency']

            if officer_uid or agency:
                docid = row['docid']
                hrg_no = row['hrg_no']
                matched_uid = officer_uid

                document = document_mappings.get((docid, hrg_no, matched_uid))
                document_id = document.get('id') if document else None

                if document_id:
                    if officer_uid:
                        officer_id = officer_mappings.get(officer_uid)
                        if officer_id:
                            officer_relation_ids[document_id] = officer_id

                    if agency:
                        formatted_agency = self.format_agency(agency)
                        department_id = department_mappings.get(formatted_agency)
                        if department_id:
                            department_relation_ids[document_id] = department_id

        department_relations = [
            DepartmentRelation(document_id=document_id, department_id=department_id)
            for document_id, department_id in department_relation_ids.items()
        ]

        officer_relations = [
            OfficerRelation(document_id=document_id, officer_id=officer_id)
            for document_id, officer_id in officer_relation_ids.items()
        ]

        DepartmentRelation.objects.all().delete()
        DepartmentRelation.objects.bulk_create(department_relations, batch_size=self.BATCH_SIZE)

        OfficerRelation.objects.all().delete()
        OfficerRelation.objects.bulk_create(officer_relations, batch_size=BATCH_SIZE)

    def generate_preview_image(self, image_blob, upload_url):
        preview_url_location = upload_url.replace('.pdf', '-preview.jpeg').replace('.PDF', '-preview.jpeg')
        preview_image_blob = generate_from_blob(image_blob)

        if preview_image_blob:
            return self.upload_file(preview_url_location, preview_image_blob, 'image/jpeg')

    def upload_file(self, upload_location, file_blob, file_type):
        try:
            self.gs.upload_file_from_string(upload_location, file_blob, file_type)

            download_url = f"{GC_PATH}{upload_location}".replace(' ', '%20').replace("'", '%27')

            return download_url
        except Exception:
            pass

    def get_ocr_text(self, ocr_text_id):
        try:
            download_url = self.ds.get_temporary_link_from_path(ocr_text_id)
            print(download_url)
            return urlopen(download_url).read().decode('utf-8')
        except Exception:
            return ''

    def clean_up_document(self, document):
        document_url = document.get('url')
        document_preview_url = document.get('preview_image_url')

        if document_url:
            try:
                self.gs.delete_file_from_url(document_url.replace(GC_PATH, ''))
            except Exception:
                pass

        if document_preview_url:
            try:
                self.gs.delete_file_from_url(document_preview_url.replace(GC_PATH, ''))
            except Exception:
                pass

    def clean_up_documents(self, documents):
        for document in documents:
            self.clean_up_document(document)

    def import_data(self, data):
        new_documents = []
        update_documents = []
        new_docids = []

        document_mappings = self.document_mappings()

        uploaded_files = {}

        for row in tqdm(data):
            document_data = self.parse_row_data(row)
            document_data['document_type'] = 'pdf'
            document_data['pages_count'] = row['page_count'] if row['page_count'] else None
            document_data['incident_date'] = parse_date(row['year'], row['month'], row['day'])
            pdf_db_path = row['pdf_db_path']

            should_upload_file = False

            docid = row['docid']if row['docid'] else None
            hrg_no = row['hrg_no'] if row['hrg_no'] else None
            matched_uid = row['matched_uid'] if row['matched_uid'] else None

            old_document = document_mappings.get((docid, hrg_no, matched_uid))

            document = {
                **(old_document or {}),
                **document_data
            }

            if old_document:
                if row['pdf_db_content_hash'] != old_document.get('pdf_db_content_hash'):
                    should_upload_file = True
                    self.clean_up_document(old_document)
            elif (docid, hrg_no, matched_uid) not in new_docids:
                should_upload_file = True

            if should_upload_file:
                try:
                    if pdf_db_path in uploaded_files:
                        uploaded_file = uploaded_files[pdf_db_path]
                        document['url'] = uploaded_file['document_url']
                        document['preview_image_url'] = uploaded_file['document_preview_url']
                    else:
                        upload_url = pdf_db_path.replace('/PPACT/', '')

                        download_url = self.ds.get_temporary_link_from_path(pdf_db_path.replace('/PPACT/', '/LLEAD/'))
                        image_blob = urlopen(download_url).read()

                        document_url = self.upload_file(upload_url, image_blob, 'application/pdf')

                        if not document_url:
                            continue
                        document['url'] = document_url

                        document_preview_url = self.generate_preview_image(image_blob, upload_url)
                        if document_preview_url:
                            document['preview_image_url'] = document_preview_url

                        uploaded_url = {
                            'document_url': document_url,
                            'document_preview_url': document_preview_url
                        }

                        uploaded_files[pdf_db_path] = uploaded_url
                except ApiError:
                    raise ValueError(f'Error downloading dropbox file from path: {pdf_db_path}')

            hrg_text = row['hrg_text']
            if hrg_text:
                document['text_content'] = hrg_text
            else:
                old_txt_db_content_hash = old_document.get('txt_db_content_hash') if old_document else None
                if row['txt_db_content_hash'] != old_txt_db_content_hash:
                    ocr_text = self.get_ocr_text(row['txt_db_id'].replace('/PPACT/', '/LLEAD/'))
                    document['text_content'] = ocr_text

            if old_document:
                update_documents.append(document)
            elif (docid, hrg_no, matched_uid) not in new_docids:
                new_docids.append((docid, hrg_no, matched_uid))
                new_documents.append(document)

        import_result = self.bulk_import(Document, new_documents, update_documents, self.clean_up_documents)

        self.update_relations(data)

        return import_result
