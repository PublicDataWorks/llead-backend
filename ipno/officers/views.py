from django.db.models import Prefetch
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control


from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from officers.constants import OFFICERS_LIMIT
from officers.models import Officer
from officers.queries import OfficerTimelineQuery, OfficerDatafileQuery
from officers.serializers import OfficerDetailsSerializer
from shared.serializers import OfficerSerializer


class OfficersViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(settings.VIEW_CACHING_TIME))
    @cache_control(no_store=True)
    def list(self, request):
        other_prefetches = (
            Prefetch(
                'department',
            ),
        )

        officers = Officer.objects.prefetch_events(other_prefetches).filter(
            canonical_person__isnull=False
        ).order_by(
            '-person__all_complaints_count'
        )[:OFFICERS_LIMIT]

        serializer = OfficerSerializer(officers, many=True)
        return Response(serializer.data)

    @method_decorator(cache_page(settings.VIEW_CACHING_TIME))
    @cache_control(no_store=True)
    def retrieve(self, request, pk):
        officer = get_object_or_404(
            Officer.objects.prefetch_related('person__canonical_officer'), id=pk
        )
        serializer = OfficerDetailsSerializer(officer.person.canonical_officer)

        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='timeline')
    @method_decorator(cache_page(settings.VIEW_CACHING_TIME))
    @cache_control(no_store=True)
    def timeline(self, request, pk):
        officer = get_object_or_404(Officer.objects.prefetch_related('person__officers'), id=pk)

        return Response(OfficerTimelineQuery(officer).query())

    @action(detail=True, methods=['get'], url_path='download-xlsx')
    def download_xlsx(self, request, pk):
        officer = get_object_or_404(Officer, id=pk)

        excel_file = OfficerDatafileQuery(officer).generate_sheets_file()
        filename = f'officer-{pk}.xlsx'

        response = HttpResponse(excel_file.getvalue(),
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response
