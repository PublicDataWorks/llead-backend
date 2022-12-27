from rest_framework import serializers


class OfficerMovementSerializer(serializers.Serializer):
    start_node = serializers.CharField(source="start_department.slug")
    end_node = serializers.CharField(source="end_department.slug")
    start_location = serializers.SerializerMethodField()
    end_location = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()
    date = serializers.CharField()
    officer_name = serializers.CharField(source="officer.name")
    officer_id = serializers.IntegerField(source="officer.id")
    left_reason = serializers.CharField()
    is_left = serializers.BooleanField(default=None)

    def get_year(self, obj):
        return obj.date.year

    def get_start_location(self, obj):
        return obj.start_department.location

    def get_end_location(self, obj):
        return obj.end_department.location
