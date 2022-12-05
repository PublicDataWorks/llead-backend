from rest_framework import serializers

from shared.serializers.document_with_text_content_serializer import (
    DocumentWithTextContentSerializer,
)


class DocumentSearchSerializer(DocumentWithTextContentSerializer):
    text_content_highlight = serializers.SerializerMethodField()

    def get_text_content_highlight(self, obj):
        try:
            return obj.es_doc.meta.highlight.text_content[0]
        except AttributeError:
            return
