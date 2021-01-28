from django.db.models import Prefetch, F, Q

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from documents.models import Document
from officers.models import OfficerHistory
from documents.serializers import DocumentSerializer
from documents.constants import DOCUMENTS_LIMIT


class DocumentsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        officer_histories = OfficerHistory.objects.filter(
            start_date__isnull=False,
            officer__document__incident_date__isnull=False,
            start_date__lte=F('officer__document__incident_date'),
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=F('officer__document__incident_date')),
        ).prefetch_related('department')

        documents = Document.objects.all().prefetch_related(
            Prefetch('officers__officerhistory_set', queryset=officer_histories, to_attr='prefetched_officer_histories')
        ).order_by(
            '-created_at'
        )[:DOCUMENTS_LIMIT]

        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)
