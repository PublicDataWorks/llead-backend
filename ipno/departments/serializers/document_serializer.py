from rest_framework import serializers

from shared.constants import TEXT_CONTENT_LIMIT


class DocumentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    document_type = serializers.CharField()
    title = serializers.CharField()
    url = serializers.CharField()
    incident_date = serializers.DateField()
    text_content = serializers.SerializerMethodField()

    def get_text_content(self, obj):
        return (obj.text_content or '')[:TEXT_CONTENT_LIMIT]
