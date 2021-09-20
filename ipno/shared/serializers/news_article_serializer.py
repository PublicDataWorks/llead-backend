from rest_framework import serializers

from news_articles.models import NewsArticleSource


class NewsArticleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    source_name = serializers.SerializerMethodField()
    title = serializers.CharField()
    url = serializers.CharField()
    date = serializers.DateField(source='published_date')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.news_article_source_name_mapping = {
            item.source_name: item.custom_matching_name for item in NewsArticleSource.objects.all()
        }

    def get_source_name(self, obj):
        return self.news_article_source_name_mapping.get(obj.source_name, obj.source_name)
