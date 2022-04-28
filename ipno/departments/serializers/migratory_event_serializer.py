from rest_framework import serializers


class MigratoryEventSerializer(serializers.Serializer):
    start_node = serializers.CharField()
    end_node = serializers.CharField()
    start_location = serializers.SerializerMethodField()
    end_location = serializers.SerializerMethodField()
    year = serializers.IntegerField()
    date = serializers.CharField()
    officer_name = serializers.CharField()
    officer_id = serializers.CharField()

    def get_start_location(self, obj):
        return obj['start_location']

    def get_end_location(self, obj):
        return obj['end_location']
