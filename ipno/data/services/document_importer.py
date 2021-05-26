from tqdm import tqdm

from documents.models import Document
from data.services.base_importer import BaseImporter
from data.constants import DOCUMENT_MODEL_NAME
from utils.parse_utils import parse_int, parse_date

BATCH_SIZE = 1000


class DocumentImporter(BaseImporter):
    data_model = DOCUMENT_MODEL_NAME
    ATTRIBUTES = [
        'docid',
        'fileid',
        'file_db_path',
        'year',
        'month',
        'day',
        'accused',
    ]
    INT_ATTRIBUTES = [
        'year',
        'month',
        'day',
    ]
    UPDATE_ATTRIBUTES = ATTRIBUTES + INT_ATTRIBUTES + [
        'title',
        'document_type',
        'url',
        'preview_image_url',
        'incident_date',
        'text_content',
        'pages_count',
    ]

    def document_mappings(self):
        return {document.docid: document.id for document in Document.objects.only('id', 'docid')}

    def update_relations(self, documents):
        OfficerRelation = Document.officers.through
        officer_relation_ids = {}

        officer_mappings = self.officer_mappings()

        for document in tqdm(documents):
            officer_uid = document.officer_uid

            if officer_uid:
                officer_id = officer_mappings.get(officer_uid)
                if officer_id:
                    officer_relation_ids[document.id] = officer_id

        officer_relations = [
            OfficerRelation(document_id=document_id, officer_id=officer_id)
            for document_id, officer_id in officer_relation_ids.items()
        ]
        OfficerRelation.objects.all().delete()
        OfficerRelation.objects.bulk_create(officer_relations, batch_size=BATCH_SIZE)

    def import_data(self, data):
        new_documents = []
        update_documents = []
        new_docids = []

        document_mappings = self.document_mappings()
        for row in tqdm(data):
            document_data = self.parse_row_data(row)
            document_data['document_type'] = 'pdf'
            document_data['pages_count'] = row['page_count'] if row['page_count'] else None
            document_data['text_content'] = row['ocr_text']
            file_path = row['file_db_path']
            document_data['incident_date'] = parse_date(row['year'], row['month'], row['day'])
            document_data['title'] = file_path.split('/')[-1].replace('.pdf', '').replace('_', ' ')

            docid = row['docid']
            document_id = document_mappings.get(docid)
            document = Document(**document_data)

            if document_id:
                document.id = document_id
                update_documents.append(document)
            elif docid not in new_docids:
                new_docids.append(docid)
                new_documents.append(document)

            officer_uid = row['matched_uid']
            setattr(document, 'officer_uid', officer_uid)

        update_document_ids = [document.id for document in update_documents]
        delete_documents = Document.objects.exclude(id__in=update_document_ids)
        delete_documents_count = delete_documents.count()
        delete_documents.delete()

        created_documents = Document.objects.bulk_create(new_documents, batch_size=BATCH_SIZE)
        Document.objects.bulk_update(update_documents, self.UPDATE_ATTRIBUTES, batch_size=BATCH_SIZE)
        self.update_relations(created_documents + update_documents)

        return {
            'created_rows': len(new_documents),
            'updated_rows': len(update_documents),
            'deleted_rows': delete_documents_count,
        }
