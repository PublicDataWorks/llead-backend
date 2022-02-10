from shared.serializers.es_serializers.base_es_serializer import BaseESSerializer
from shared.serializers import DocumentSearchSerializer
from documents.models import Document


class DepartmentDocumentsESSerializer(BaseESSerializer):
    serializer = DocumentSearchSerializer
    model_klass = Document

    def get_queryset(self, ids):
        return self.model_klass.objects.prefetch_departments().filter(id__in=ids)
