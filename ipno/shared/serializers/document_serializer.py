from rest_framework import serializers

from shared.serializers.simple_department_serializer import SimpleDepartmentSerializer


class DocumentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    document_type = serializers.CharField()
    title = serializers.CharField()
    url = serializers.CharField()
    incident_date = serializers.DateField()
    preview_image_url = serializers.CharField()
    pages_count = serializers.IntegerField()
    departments = SimpleDepartmentSerializer(many=True)
