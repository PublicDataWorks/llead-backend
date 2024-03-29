from rest_framework import serializers


class NewsArticleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    source_name = serializers.CharField(source="source.source_display_name")
    title = serializers.CharField()
    url = serializers.CharField()
    date = serializers.DateField(source="published_date")
    author = serializers.CharField()
