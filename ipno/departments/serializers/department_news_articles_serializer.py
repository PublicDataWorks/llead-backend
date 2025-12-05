from rest_framework import serializers


class DepartmentNewsArticleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    published_date = serializers.DateField()
    url = serializers.CharField()
    is_starred = serializers.BooleanField()

    source_display_name = serializers.SerializerMethodField()

    def get_source_display_name(self, obj):
        return obj.source.source_display_name if obj.source else None
