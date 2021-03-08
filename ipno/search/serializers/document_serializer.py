from rest_framework import serializers

from shared.serializers import (
    DocumentWithDepartmentsSerializer,
    BaseDocumentSearchSerializer,
)


class DocumentSerializer(
    DocumentWithDepartmentsSerializer,
    BaseDocumentSearchSerializer
):
    id = serializers.IntegerField()
    document_type = serializers.CharField()
    title = serializers.CharField()
    url = serializers.CharField()
    incident_date = serializers.DateField()
