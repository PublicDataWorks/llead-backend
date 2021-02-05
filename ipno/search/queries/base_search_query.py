from search.constants import SEARCH_LIMIT


class BaseSearchQuery(object):
    document_klass = None
    fields = []

    def query(self, query):
        return self.document_klass().search() \
            .query('multi_match', query=query, operator='and', fields=self.fields)

    def search(self, query, size=SEARCH_LIMIT, begin=0):
        return self.query(query)[begin:size].execute()
