from .base_es_serializer import BaseESSerializer
from search.serializers import DocumentSerializer
from documents.models import Document


class DocumentsESSerializer(BaseESSerializer):
    serializer = DocumentSerializer
    model_klass = Document

    def get_queryset(self, ids):
        return self.model_klass.objects.prefetch_departments().filter(id__in=ids)
