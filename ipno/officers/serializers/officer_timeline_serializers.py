from rest_framework import serializers

from shared.serializers import DocumentSerializer

from utils.parse_utils import parse_date

from officers.constants import (
    JOINED_TIMELINE_KIND,
    LEFT_TIMELINE_KIND,
    COMPLAINT_TIMELINE_KIND,
    DOCUMENT_TIMELINE_KIND,
    SALARY_CHANGE_TIMELINE_KIND,
    RANK_CHANGE_TIMELINE_KIND
)


class BaseTimelineSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    date = serializers.SerializerMethodField()
    kind = serializers.SerializerMethodField()

    def get_kind(self, obj):
        raise NotImplementedError

    def get_date(self, obj):
        date = parse_date(obj.year, obj.month, obj.day)
        return str(date) if date else None


class JoinedTimelineSerializer(BaseTimelineSerializer):
    def get_kind(self, obj):
        return JOINED_TIMELINE_KIND


class LeftTimelineSerializer(BaseTimelineSerializer):
    def get_kind(self, obj):
        return LEFT_TIMELINE_KIND


class ComplaintTimelineSerializer(BaseTimelineSerializer):
    id = serializers.IntegerField()
    date = serializers.DateField(source='incident_date')
    year = serializers.IntegerField(source='occur_year')
    rule_violation = serializers.CharField()
    paragraph_violation = serializers.CharField()
    disposition = serializers.CharField()
    action = serializers.CharField()
    tracking_number = serializers.CharField()

    def get_kind(self, obj):
        return COMPLAINT_TIMELINE_KIND


class DocumentTimelineSerializer(DocumentSerializer, BaseTimelineSerializer):
    date = serializers.DateField(source='incident_date')
    year = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return DOCUMENT_TIMELINE_KIND

    def get_year(self, obj):
        return obj.incident_date.year if obj.incident_date else None


class SalaryChangeTimelineSerializer(BaseTimelineSerializer):
    annual_salary = serializers.CharField()

    def get_kind(self, obj):
        return SALARY_CHANGE_TIMELINE_KIND


class RankChangeTimelineSerializer(BaseTimelineSerializer):
    rank_desc = serializers.CharField()

    def get_kind(self, obj):
        return RANK_CHANGE_TIMELINE_KIND
