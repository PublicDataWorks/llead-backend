from django.http import HttpResponse
from django.shortcuts import get_object_or_404

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

    def list(self, request):
        officers = Officer.objects.prefetch_events().filter(
            canonical_person__isnull=False
        ).order_by(
            '-person__all_complaints_count'
        )[:OFFICERS_LIMIT]

        serializer = OfficerSerializer(officers, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk):
        officer = get_object_or_404(Officer.objects.prefetch_related('person__canonical_officer'), id=pk)
        serializer = OfficerDetailsSerializer(officer.person.canonical_officer)

        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='timeline')
    def timeline(self, request, pk):
        officer = get_object_or_404(Officer, id=pk)

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
