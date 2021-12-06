from search.queries.news_articles_search_query import NewsArticlesSearchQuery
from search.queries.departments_search_query import DepartmentsSearchQuery
from search.queries.officers_search_query import OfficersSearchQuery
from search.queries.documents_search_query import DocumentsSearchQuery
from search.serializers.es_serializers import DepartmentsESSerializer, OfficersESSerializer
from shared.serializers.es_serializers import DocumentsESSerializer
from shared.serializers.es_serializers import NewsArticlesESSerializer
from utils.es_pagination import ESPagination

SEARCH_MAPPINGS = {
    'departments': {
        'search_query': DepartmentsSearchQuery,
        'serializer': DepartmentsESSerializer,
    },
    'officers': {
        'search_query': OfficersSearchQuery,
        'serializer': OfficersESSerializer,
    },
    'documents': {
        'search_query': DocumentsSearchQuery,
        'serializer': DocumentsESSerializer,
    },
    'articles': {
        'search_query': NewsArticlesSearchQuery,
        'serializer': NewsArticlesESSerializer,
    }
}


class SearchAllQuery(object):
    def __init__(self, request):
        self.request = request

    def search(self, query, doc_type, department=None):
        results = {}

        doc_section = SEARCH_MAPPINGS.get(doc_type)
        sections = {doc_type: doc_section} if doc_section else SEARCH_MAPPINGS
        paginator = ESPagination()

        for search_key, search_mapping in sections.items():
            search_query = search_mapping['search_query'](query, department)
            search_result = paginator.paginate_es_query(search_query, self.request)

            data = search_mapping['serializer'](search_result).data
            results[search_key] = {
                'count': paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'results': data,
            }

        return results
