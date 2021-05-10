from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from documents.models import Document
from officers.models import Officer
from departments.models import Department

from shared.serializers import DepartmentSerializer, OfficerSerializer
from shared.serializers import DocumentSerializer


class HistoricalDataViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='recent-items')
    def recent_items(self, request):
        recent_items_queries = [
            {
                'item_type': 'department',
                'query': Department.objects.all(),
                'serializer': DepartmentSerializer,
                'key': 'slug',
            },
            {
                'item_type': 'officer',
                'query': Officer.objects.prefetch_events(),
                'serializer': OfficerSerializer,
            },
            {
                'item_type': 'document',
                'query': Document.objects.prefetch_departments(),
                'serializer': DocumentSerializer,
            },
        ]

        recent_search_data = {}
        for recent_items_query in recent_items_queries:
            item_type = recent_items_query['item_type']
            item_key = recent_items_query.get('key', 'id')
            ids = self.request.query_params.getlist(f'{item_type}_ids[]', None)
            if ids:
                items = recent_items_query['query'].filter(**{f'{item_key}__in': ids})
                recent_search_data[item_type] = recent_items_query['serializer'](items, many=True).data

        return Response(recent_search_data)
