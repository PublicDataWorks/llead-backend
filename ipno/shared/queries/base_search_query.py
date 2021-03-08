from shared.constants import SEARCH_LIMIT


class BaseSearchQuery(object):
    document_klass = None
    fields = []

    def __init__(self, q, **kwargs):
        self.q = q

    def query(self):
        return self.document_klass().search() \
            .query('multi_match', query=self.q, operator='and', fields=self.fields)

    def search(self, size=SEARCH_LIMIT, begin=0):
        return self.query()[begin:begin + size].execute()
