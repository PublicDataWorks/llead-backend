from rest_framework import serializers


class DepartmentDocumentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    is_starred = serializers.BooleanField()

    title = serializers.CharField()
    url = serializers.CharField()
    incident_date = serializers.DateField()
    preview_image_url = serializers.CharField()
    pages_count = serializers.IntegerField()
