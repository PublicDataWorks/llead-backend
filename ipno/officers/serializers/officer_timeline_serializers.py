from rest_framework import serializers

from shared.serializers import DocumentSerializer

from utils.parse_utils import parse_date

from officers.constants import (
    JOINED_TIMELINE_KIND,
    LEFT_TIMELINE_KIND,
    COMPLAINT_TIMELINE_KIND,
    UOF_TIMELINE_KIND,
    DOCUMENT_TIMELINE_KIND,
    SALARY_CHANGE_TIMELINE_KIND,
    RANK_CHANGE_TIMELINE_KIND,
    UNIT_CHANGE_TIMELINE_KIND,
    NEWS_ARTICLE_TIMELINE_KIND,
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
    department = serializers.CharField(source='department.name')

    def get_kind(self, obj):
        return JOINED_TIMELINE_KIND


class LeftTimelineSerializer(BaseTimelineSerializer):
    department = serializers.CharField(source='department.name')

    def get_kind(self, obj):
        return LEFT_TIMELINE_KIND


class ComplaintTimelineSerializer(BaseTimelineSerializer):
    year = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    rule_code = serializers.CharField()
    rule_violation = serializers.CharField()
    paragraph_code = serializers.CharField()
    paragraph_violation = serializers.CharField()
    disposition = serializers.CharField()
    action = serializers.CharField()
    tracking_number = serializers.CharField()
    allegation_desc = serializers.CharField()

    def _get_receive_event(self, obj):
        if not hasattr(obj, 'receive_event'):
            event = None
            if obj.prefetched_receive_events:
                event = obj.prefetched_receive_events[0]
            setattr(obj, 'receive_event', event)
        return obj.receive_event

    def get_kind(self, obj):
        return COMPLAINT_TIMELINE_KIND

    def get_date(self, obj):
        receive_event = self._get_receive_event(obj)
        if receive_event:
            date = parse_date(receive_event.year, receive_event.month, receive_event.day)
            return str(date) if date else None

    def get_year(self, obj):
        receive_event = self._get_receive_event(obj)
        return receive_event.year if receive_event else None


class UseOfForceTimelineSerializer(BaseTimelineSerializer):
    year = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    force_type = serializers.CharField()
    force_description = serializers.CharField()
    force_reason = serializers.CharField()
    disposition = serializers.CharField()
    service_type = serializers.CharField()
    citizen_involvement = serializers.CharField()
    citizen_age = serializers.IntegerField()
    citizen_race = serializers.CharField()
    citizen_sex = serializers.CharField()
    uof_tracking_number = serializers.CharField()
    citizen_arrested = serializers.CharField()
    citizen_injured = serializers.CharField()
    citizen_hospitalized = serializers.CharField()
    officer_injured = serializers.CharField()
    traffic_stop = serializers.CharField()

    def get_kind(self, obj):
        return UOF_TIMELINE_KIND

    def _get_receive_event(self, obj):
        if not hasattr(obj, 'receive_event'):
            event = None
            if obj.events.all():
                event = obj.events.all()[0]
            setattr(obj, 'receive_event', event)
        return obj.receive_event

    def get_date(self, obj):
        receive_event = self._get_receive_event(obj)
        if receive_event:
            date = parse_date(receive_event.year, receive_event.month, receive_event.day)
            return str(date) if date else None

    def get_year(self, obj):
        receive_event = self._get_receive_event(obj)
        return receive_event.year if receive_event else None


class DocumentTimelineSerializer(DocumentSerializer, BaseTimelineSerializer):
    date = serializers.DateField(source='incident_date')
    year = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return DOCUMENT_TIMELINE_KIND

    def get_year(self, obj):
        return obj.incident_date.year if obj.incident_date else None


class NewsArticleTimelineSerializer(BaseTimelineSerializer):
    id = serializers.IntegerField()
    source_name = serializers.CharField(source='source.source_display_name')
    title = serializers.CharField()
    url = serializers.CharField()
    date = serializers.DateField(source='published_date')
    year = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return NEWS_ARTICLE_TIMELINE_KIND

    def get_year(self, obj):
        return obj.published_date.year if obj.published_date else None


class SalaryChangeTimelineSerializer(BaseTimelineSerializer):
    salary = serializers.CharField()
    salary_freq = serializers.CharField()

    def get_kind(self, obj):
        return SALARY_CHANGE_TIMELINE_KIND


class RankChangeTimelineSerializer(BaseTimelineSerializer):
    rank_code = serializers.CharField()
    rank_desc = serializers.CharField()

    def get_kind(self, obj):
        return RANK_CHANGE_TIMELINE_KIND


class UnitChangeTimelineSerializer(BaseTimelineSerializer):
    department_code = serializers.CharField()
    department_desc = serializers.CharField()
    prev_department_code = serializers.CharField(default=None)
    prev_department_desc = serializers.CharField(default=None)

    def get_kind(self, obj):
        return UNIT_CHANGE_TIMELINE_KIND
