from rest_framework import serializers


class NewsArticleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    source_name = serializers.SerializerMethodField()
    title = serializers.CharField()
    url = serializers.CharField()
    date = serializers.DateField(source="published_date")
    author = serializers.CharField()

    def get_source_name(self, obj):
        return obj.source.source_display_name if obj.source else None
