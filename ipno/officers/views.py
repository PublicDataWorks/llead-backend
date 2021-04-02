from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from officers.models import Officer
from shared.serializers import OfficerSerializer
from officers.serializers import OfficerDetailsSerializer
from officers.constants import OFFICERS_LIMIT
from shared.serializers import DocumentWithTextContentSerializer
from officers.queries import OfficerTimelineQuery


class OfficersViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        officers = Officer.objects.prefetch_officer_histories().order_by(
            '-created_at'
        )[:OFFICERS_LIMIT]

        serializer = OfficerSerializer(officers, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk):
        officer = get_object_or_404(Officer, id=pk)
        serializer = OfficerDetailsSerializer(officer)

        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='timeline')
    def timeline(self, request, pk):
        officer = get_object_or_404(Officer, id=pk)

        return Response(OfficerTimelineQuery(officer).query())

    @action(detail=True, methods=['get'], url_path='documents')
    def documents(self, request, pk):
        officer = get_object_or_404(Officer, id=pk)
        documents = officer.document_set.prefetch_departments().order_by('-incident_date')

        serializer = DocumentWithTextContentSerializer(documents, many=True)
        return Response(serializer.data)
