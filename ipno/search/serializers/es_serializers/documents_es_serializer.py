from django.db.models import Prefetch, F, Q

from .base_es_serializer import BaseESSerializer
from search.serializers import DocumentSerializer
from officers.models import OfficerHistory
from documents.models import Document


class DocumentsESSerializer(BaseESSerializer):
    serializer = DocumentSerializer
    model_klass = Document

    def get_queryset(self, ids):
        officer_histories = OfficerHistory.objects.filter(
            start_date__isnull=False,
            officer__document__incident_date__isnull=False,
            start_date__lte=F('officer__document__incident_date'),
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=F('officer__document__incident_date')),
        ).prefetch_related('department')

        return super(DocumentsESSerializer, self).get_queryset(ids).prefetch_related(
            'departments',
            Prefetch('officers__officerhistory_set', queryset=officer_histories, to_attr='prefetched_officer_histories')
        )
