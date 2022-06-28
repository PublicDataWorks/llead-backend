from shared.queries.base_search_query import BaseSearchQuery
from officers.documents import OfficerESDoc


class OfficersSearchQuery(BaseSearchQuery):
    document_klass = OfficerESDoc
    fields = ['name']

    def query(self, order=None):
        search = self.document_klass().search()
        if self.department:
            search = search.query('match_phrase', department_slug=self.department)
        if not order:
            return search.query('multi_match', query=self.q, operator='and', fields=self.fields)
        else:
            return search.sort(order).query(
                'multi_match',
                query=self.q,
                operator='and',
                fields=self.fields
            )
