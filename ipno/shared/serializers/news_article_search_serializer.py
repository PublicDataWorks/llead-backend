from rest_framework import serializers

from shared.serializers.news_article_with_text_content_serializer import (
    NewsArticleWithTextContentSerializer,
)


class NewsArticleSearchSerializer(NewsArticleWithTextContentSerializer):
    content_highlight = serializers.SerializerMethodField()
    author_highlight = serializers.SerializerMethodField()

    def get_content_highlight(self, obj):
        try:
            return obj.es_doc.meta.highlight.content[0]
        except AttributeError:
            return

    def get_author_highlight(self, obj):
        try:
            return obj.es_doc.meta.highlight.author[0]
        except AttributeError:
            return
