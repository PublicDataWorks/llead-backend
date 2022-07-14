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
    APPEAL_TIMELINE_KIND,
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
    disposition = serializers.CharField()
    action = serializers.CharField()
    tracking_id = serializers.CharField()
    allegation = serializers.CharField()
    allegation_desc = serializers.CharField()
    citizen_arrested = serializers.CharField()
    traffic_stop = serializers.CharField()

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
    use_of_force_description = serializers.CharField()
    use_of_force_reason = serializers.SerializerMethodField()
    disposition = serializers.SerializerMethodField()
    service_type = serializers.SerializerMethodField()
    citizen_information = serializers.SerializerMethodField()
    tracking_id = serializers.SerializerMethodField()
    citizen_arrested = serializers.SerializerMethodField()
    citizen_injured = serializers.SerializerMethodField()
    citizen_hospitalized = serializers.SerializerMethodField()
    officer_injured = serializers.CharField()

    def get_kind(self, obj):
        return UOF_TIMELINE_KIND

    def _get_receive_event(self, obj):
        if not hasattr(obj, 'receive_event'):
            event = None
            if obj.use_of_force.events.all():
                event = obj.use_of_force.events.all()[0]
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

    def get_use_of_force_reason(self, obj):
        return obj.use_of_force.use_of_force_reason

    def get_disposition(self, obj):
        return obj.use_of_force.disposition

    def get_service_type(self, obj):
        return obj.use_of_force.service_type

    def get_citizen_information(self, obj):
        return [o.citizen_age + '-year-old ' + o.citizen_race + ' ' + o.citizen_sex if o.citizen_age
                else o.citizen_race + ' ' + o.citizen_sex for o in obj.use_of_force.uof_citizens.all()]

    def get_tracking_id(self, obj):
        return obj.use_of_force.tracking_id

    def get_citizen_arrested(self, obj):
        arrests = [o.citizen_arrested for o in obj.use_of_force.uof_citizens.all()]

        return arrests

    def get_citizen_injured(self, obj):
        injures = [o.citizen_injured for o in obj.use_of_force.uof_citizens.all()]

        return injures

    def get_citizen_hospitalized(self, obj):
        hospitals = [o.citizen_hospitalized for o in obj.use_of_force.uof_citizens.all()]

        return hospitals


class AppealTimelineSerializer(BaseTimelineSerializer):
    year = serializers.SerializerMethodField()
    department = serializers.CharField(source='department.name')
    id = serializers.IntegerField()
    docket_no = serializers.CharField()
    counsel = serializers.CharField()
    charging_supervisor = serializers.CharField()
    appeal_disposition = serializers.CharField()
    action_appealed = serializers.CharField()
    appealed = serializers.CharField()
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
