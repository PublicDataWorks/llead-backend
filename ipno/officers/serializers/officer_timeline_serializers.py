from rest_framework import serializers

from officers.constants import (
    JOINED_TIMELINE_TYPE,
    LEFT_TIMELINE_TYPE,
    COMPLAINT_TIMELINE_TYPE,
)


class BaseTimelineSerializer(serializers.Serializer):
    kind = serializers.SerializerMethodField()

    def get_kind(self, obj):
        raise NotImplementedError


class JoinedTimelineSerializer(BaseTimelineSerializer):
    date = serializers.DateField(source='start_date', format=None)
    year = serializers.IntegerField(source='hire_year')

    def get_kind(self, obj):
        return JOINED_TIMELINE_TYPE


class LeftTimelineSerializer(BaseTimelineSerializer):
    date = serializers.DateField(source='end_date', format=None)
    year = serializers.IntegerField(source='term_year')

    def get_kind(self, obj):
        return LEFT_TIMELINE_TYPE


class ComplaintTimelineSerializer(BaseTimelineSerializer):
    date = serializers.DateField(source='incident_date', format=None)
    year = serializers.IntegerField(source='occur_year')
    rule_violation = serializers.CharField()
    paragraph_violation = serializers.CharField()
    disposition = serializers.CharField()
    action = serializers.CharField()
    tracking_number = serializers.CharField()

    def get_kind(self, obj):
        return COMPLAINT_TIMELINE_TYPE
