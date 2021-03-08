from rest_framework import serializers

from search.constants import TEXT_CONTENT_LIMIT


class BaseDocumentSearchSerializer(serializers.Serializer):
    text_content = serializers.SerializerMethodField()
    text_content_highlight = serializers.SerializerMethodField()

    def get_text_content(self, obj):
        return (obj.text_content or '')[:TEXT_CONTENT_LIMIT]

    def get_text_content_highlight(self, obj):
        try:
            return obj.es_doc.meta.highlight.text_content[0]
        except AttributeError:
            return
