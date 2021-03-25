from rest_framework import serializers

from shared.serializers.document_serializer import DocumentSerializer
from shared.constants import TEXT_CONTENT_LIMIT


class DocumentWithTextContentSerializer(DocumentSerializer):
    text_content = serializers.SerializerMethodField()

    def get_text_content(self, obj):
        return (obj.text_content or '')[:TEXT_CONTENT_LIMIT]
