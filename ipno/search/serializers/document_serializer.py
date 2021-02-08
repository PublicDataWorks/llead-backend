from rest_framework import serializers

from shared.serializers import BaseDocumentSerializer


class DocumentSerializer(BaseDocumentSerializer):
    text_content = serializers.CharField()
    text_content_highlight = serializers.SerializerMethodField()

    def get_text_content_highlight(self, obj):
        try:
            return obj.es_doc.meta.highlight.text_content[0]
        except AttributeError:
            return
