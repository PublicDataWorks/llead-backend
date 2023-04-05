from rest_framework import serializers

from officers.constants import (
    APPEAL_TIMELINE_KIND,
    COMPLAINT_TIMELINE_KIND,
    DOCUMENT_TIMELINE_KIND,
    JOINED_TIMELINE_KIND,
    LEFT_TIMELINE_KIND,
    NEWS_ARTICLE_TIMELINE_KIND,
    RANK_CHANGE_TIMELINE_KIND,
    SALARY_CHANGE_TIMELINE_KIND,
    UNIT_CHANGE_TIMELINE_KIND,
    UOF_TIMELINE_KIND,
)
from shared.serializers import DocumentSerializer
from utils.parse_utils import parse_date


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
    department = serializers.CharField(source="department.agency_name")

    def get_kind(self, obj):
        return JOINED_TIMELINE_KIND


class LeftTimelineSerializer(BaseTimelineSerializer):
    department = serializers.CharField(source="department.agency_name")

    def get_kind(self, obj):
        return LEFT_TIMELINE_KIND


class ComplaintTimelineSerializer(BaseTimelineSerializer):
    year = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    disposition = serializers.CharField()
    action = serializers.CharField()
    tracking_id = serializers.CharField()
    allegation = serializers.CharField()
    allegation_desc = serializers.CharField()

    def _get_receive_event(self, obj):
        if not hasattr(obj, "receive_event"):
            event = None
            if obj.prefetched_receive_events:
                event = obj.prefetched_receive_events[0]
            setattr(obj, "receive_event", event)
        return obj.receive_event

    def get_kind(self, obj):
        return COMPLAINT_TIMELINE_KIND

    def get_date(self, obj):
        receive_event = self._get_receive_event(obj)
        if receive_event:
            date = parse_date(
                receive_event.year, receive_event.month, receive_event.day
            )
            return str(date) if date else None

    def get_year(self, obj):
        receive_event = self._get_receive_event(obj)
        return receive_event.year if receive_event else None


class UseOfForceTimelineSerializer(BaseTimelineSerializer):
    year = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    use_of_force_description = serializers.CharField()
    use_of_force_reason = serializers.CharField()
    disposition = serializers.CharField()
    service_type = serializers.CharField()
    tracking_id = serializers.CharField()
    officer_injured = serializers.CharField()

    citizen_information = serializers.SerializerMethodField()
    citizen_arrested = serializers.SerializerMethodField()
    citizen_injured = serializers.SerializerMethodField()
    citizen_hospitalized = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return UOF_TIMELINE_KIND

    def _get_receive_event(self, obj):
        if not hasattr(obj, "receive_event"):
            event = None
            if obj.events.all():
                event = obj.events.all()[0]
            setattr(obj, "receive_event", event)
        return obj.receive_event

    def get_date(self, obj):
        receive_event = self._get_receive_event(obj)
        if receive_event:
            date = parse_date(
                receive_event.year, receive_event.month, receive_event.day
            )
            return str(date) if date else None

    def get_year(self, obj):
        receive_event = self._get_receive_event(obj)
        return receive_event.year if receive_event else None

    def get_citizen_information(self, obj):
        return [
            str(o.citizen_age) + "-year-old " + o.citizen_race + " " + o.citizen_sex
            if o.citizen_age
            else o.citizen_race + " " + o.citizen_sex
            for o in obj.citizens.all()
        ]

    def get_citizen_arrested(self, obj):
        arrests = [o.citizen_arrested for o in obj.citizens.all()]

        return arrests

    def get_citizen_injured(self, obj):
        injures = [o.citizen_injured for o in obj.citizens.all()]

        return injures

    def get_citizen_hospitalized(self, obj):
        hospitals = [o.citizen_hospitalized for o in obj.citizens.all()]

        return hospitals


class AppealTimelineSerializer(BaseTimelineSerializer):
    year = serializers.SerializerMethodField()
    department = serializers.CharField(source="department.agency_name")
    id = serializers.IntegerField()
    charging_supervisor = serializers.CharField()
    appeal_disposition = serializers.CharField()
    action_appealed = serializers.CharField()
    motions = serializers.CharField()

    def get_kind(self, obj):
        return APPEAL_TIMELINE_KIND

    def get_date(self, obj):
        if obj.events.all():
            year = obj.events.all()[0].year
            month = obj.events.all()[0].month
            day = obj.events.all()[0].day
            date = parse_date(year, month, day)
            return str(date) if date else None
        return None

    def get_year(self, obj):
        return obj.events.all()[0].year if obj.events.all() else None


class DocumentTimelineSerializer(DocumentSerializer, BaseTimelineSerializer):
    date = serializers.DateField(source="incident_date")
    year = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return DOCUMENT_TIMELINE_KIND

    def get_year(self, obj):
        return obj.incident_date.year if obj.incident_date else None


class NewsArticleTimelineSerializer(BaseTimelineSerializer):
    id = serializers.IntegerField()
    source_name = serializers.CharField(source="source.source_display_name")
    title = serializers.CharField()
    url = serializers.CharField()
    date = serializers.DateField(source="published_date")
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
