from rest_framework import viewsets
from rest_framework.response import Response

from search.queries import SearchAllQuery


class SearchViewSet(viewsets.ViewSet):
    def list(self, request):
        query = self.request.query_params.get('q')
        doc_type = self.request.query_params.get('doc_type')
        department = self.request.query_params.get('department')

        return Response(SearchAllQuery(request).search(query, doc_type, department))
