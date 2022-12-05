from documents.documents import DocumentESDoc
from shared.queries.base_search_query import BaseSearchQuery


class DocumentsSearchQuery(BaseSearchQuery):
    document_klass = DocumentESDoc
    fields = [
        "title",
        "text_content",
        "officer_names",
        "officer_badges",
        "department_names",
    ]

    def query(self):
        return super(DocumentsSearchQuery, self).query().highlight("text_content")
