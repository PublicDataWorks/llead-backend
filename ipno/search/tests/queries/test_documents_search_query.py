from django.test import TestCase

from documents.factories import DocumentFactory
from search.queries.documents_search_query import DocumentsSearchQuery
from utils.search_index import rebuild_search_index


class DocumentsSearchQueryTestCase(TestCase):
    def test_query(self):
        DocumentFactory(title='Document title', text_content='Text content')
        document_1 = DocumentFactory(title='Document keyword1', text_content='Text content 1')
        document_2 = DocumentFactory(title='Document 2', text_content='Text content keyword 2')

        rebuild_search_index()

        result = DocumentsSearchQuery().search('keyword')
        document_ids = {item['id'] for item in result}

        assert document_ids == {document_1.id, document_2.id}
