from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from search.queries import SearchAllQuery


class SearchViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        query = self.request.query_params.get('q')

        return Response(SearchAllQuery().search(query))
