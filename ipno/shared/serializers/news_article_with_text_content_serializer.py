from rest_framework import serializers

from shared.constants import TEXT_CONTENT_LIMIT
from shared.serializers.news_article_serializer import NewsArticleSerializer


class NewsArticleWithTextContentSerializer(NewsArticleSerializer):
    content = serializers.SerializerMethodField()

    def get_content(self, obj):
        return (obj.content or "")[:TEXT_CONTENT_LIMIT]
