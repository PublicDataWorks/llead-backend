from shared.constants import SEARCH_LIMIT


class BaseSearchQuery(object):
    document_klass = None
    fields = []

    def __init__(self, q, department=None, **kwargs):
        self.q = q
        self.department = department

    def query(self, order=None, pre_term_query=None):
        search = self.document_klass().search()
        if pre_term_query:
            search = search.query('term', **pre_term_query)
        if self.department:
            search = search.query('match_phrase', department_slugs=self.department)
        if not order:
            return search.query('multi_match', query=self.q, operator='and', fields=self.fields)
        else:
            return search.sort(order).query(
                'multi_match',
                query=self.q,
                operator='and',
                fields=self.fields
            )

    def search(self, size=SEARCH_LIMIT, begin=0):
        return self.query()[begin:begin + size].execute()
