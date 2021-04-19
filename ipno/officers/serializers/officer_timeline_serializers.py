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
    kind = serializers.SerializerMethodField()

    def get_kind(self, obj):
        raise NotImplementedError


class JoinedTimelineSerializer(BaseTimelineSerializer):
    date = serializers.DateField(source='start_date')
    year = serializers.IntegerField(source='hire_year')

    def get_kind(self, obj):
        return JOINED_TIMELINE_KIND


class LeftTimelineSerializer(BaseTimelineSerializer):
    date = serializers.DateField(source='end_date')
    year = serializers.IntegerField(source='term_year')

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

    def get_kind(self, obj):
        return DOCUMENT_TIMELINE_KIND


class SalaryChangeTimelineSerializer(BaseTimelineSerializer):
    year = serializers.IntegerField(source='pay_effective_year')
    annual_salary = serializers.CharField()
    date = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return SALARY_CHANGE_TIMELINE_KIND

    def get_date(self, obj):
        return parse_date(
            obj.pay_effective_year,
            obj.pay_effective_month,
            obj.pay_effective_day
        )


class RankChangeTimelineSerializer(BaseTimelineSerializer):
    year = serializers.IntegerField(source='rank_year')
    rank_desc = serializers.CharField()
    date = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return RANK_CHANGE_TIMELINE_KIND

    def get_date(self, obj):
        return parse_date(obj.rank_year, obj.rank_month, obj.rank_day)
