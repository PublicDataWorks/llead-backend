from shared.serializers.es_serializers import BaseESSerializer
from departments.serializers import DocumentSearchSerializer
from documents.models import Document


class DocumentsESSerializer(BaseESSerializer):
    serializer = DocumentSearchSerializer
    model_klass = Document
