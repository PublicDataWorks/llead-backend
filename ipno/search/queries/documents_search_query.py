from .base_search_query import BaseSearchQuery
from documents.documents import DocumentESDoc


class DocumentsSearchQuery(BaseSearchQuery):
    document_klass = DocumentESDoc
    fields = ['title', 'text_content']

    def query(self, query):
        return super(DocumentsSearchQuery, self).query(query).highlight('text_content')
