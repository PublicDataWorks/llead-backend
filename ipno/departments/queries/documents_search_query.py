from documents.documents import DocumentESDoc
from shared.queries import BaseSearchQuery


class DocumentsSearchQuery(BaseSearchQuery):
    document_klass = DocumentESDoc
    fields = ['title', 'text_content', 'officer_names', 'officer_badges']

    def __init__(self, q, **kwargs):
        super(DocumentsSearchQuery, self).__init__(q, **kwargs)
        self.department_id = kwargs['department_id']

    def query(self):
        return super(DocumentsSearchQuery, self).query() \
            .filter('term', department_ids=self.department_id) \
            .highlight('text_content')
