from rest_framework import serializers

from shared.constants import TEXT_CONTENT_LIMIT
from shared.serializers.document_serializer import DocumentSerializer


class DocumentWithTextContentSerializer(DocumentSerializer):
    text_content = serializers.SerializerMethodField()

    def get_text_content(self, obj):
        return (obj.text_content or "")[:TEXT_CONTENT_LIMIT]
