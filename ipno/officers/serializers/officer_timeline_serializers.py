from rest_framework import serializers

from complaints.models import Complaint
from departments.models import Department, OfficerMovement
from officers.constants import (
    APPEAL_TIMELINE_KIND,
    BRADY_LIST_TIMELINE_KIND,
    COMPLAINT_TIMELINE_KIND,
    DOCUMENT_TIMELINE_KIND,
    FIREARM_CERTIFICATION_TIMELINE_KIND,
    JOINED_TIMELINE_KIND,
    LEFT_TIMELINE_KIND,
    NEWS_ARTICLE_TIMELINE_KIND,
    OFFICER_LEFT,
    PC_12_QUALIFICATION_TIMELINE_KIND,
    POST_DECERTIFICATION_TIMELINE_KIND,
    RANK_CHANGE_TIMELINE_KIND,
    RESIGNED_TIMELINE_KIND,
    SALARY_CHANGE_TIMELINE_KIND,
    TERMINATED_TIMELINE_KIND,
    UNIT_CHANGE_TIMELINE_KIND,
    UOF_TIMELINE_KIND,
)
from officers.models import Event, Officer
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
    left_department = serializers.SerializerMethodField()
    left_date = serializers.SerializerMethodField()
    left_reason = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return JOINED_TIMELINE_KIND

    def _get_person_officers(self, obj):
        if not hasattr(obj, "person_officers"):
            # Handle officers without person association
            if obj.officer.person:
                person_officers = obj.officer.person.officers.all()
            else:
                person_officers = [obj.officer]
            setattr(obj, "person_officers", person_officers)

        return obj.person_officers

    def _get_movement(self, obj):
        if not hasattr(obj, "movement"):
            all_officers = self._get_person_officers(obj)

            movement = OfficerMovement.objects.filter(
                officer__in=all_officers,
                end_department=obj.department,
            )

            setattr(obj, "movement", movement.first() if movement else None)

        return obj.movement

    def get_left_department(self, obj):
        movement = self._get_movement(obj)

        return movement.start_department.agency_name if movement else None

    def get_left_date(self, obj):
        left_event = None
        left_department = self.get_left_department(obj)

        if left_department:
            all_officers = self._get_person_officers(obj)

            left_event = Event.objects.filter(
                officer__in=all_officers,
                kind=OFFICER_LEFT,
                department__agency_name=left_department,
            ).first()

        return (
            str(parse_date(left_event.year, left_event.month, left_event.day))
            if left_event
            else None
        )

    def get_left_reason(self, obj):
        movement = None
        left_department = self.get_left_department(obj)

        if left_department:
            movement = self._get_movement(obj)

        return movement.left_reason if movement else None


class LeftTimelineSerializer(BaseTimelineSerializer):
    department = serializers.CharField(source="department.agency_name")

    def get_kind(self, obj):
        return LEFT_TIMELINE_KIND


class TerminatedLeftTimelineSerializer(BaseTimelineSerializer):
    department = serializers.CharField(source="department.agency_name")

    def get_kind(self, obj):
        return TERMINATED_TIMELINE_KIND


class ResignLeftTimelineSerializer(BaseTimelineSerializer):
    department = serializers.CharField(source="department.agency_name")

    def get_kind(self, obj):
        return RESIGNED_TIMELINE_KIND


class ComplaintTimelineSerializer(BaseTimelineSerializer):
    year = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    disposition = serializers.CharField()
    action = serializers.CharField()
    tracking_id = serializers.CharField()
    allegation = serializers.CharField()
    allegation_desc = serializers.CharField()
    associated_officers = serializers.SerializerMethodField()

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

    def get_associated_officers(self, obj):
        complaints = Complaint.objects.filter(
            tracking_id__isnull=False,
            tracking_id=obj.tracking_id,
        ).exclude(officers__in=obj.officers.all())

        officers = (
            Officer.objects.filter(complaints__in=complaints).order_by("id").distinct()
        )

        serialized_officers = [
            {
                "id": officer.id,
                "name": officer.name,
            }
            for officer in officers
        ]

        return serialized_officers


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


class PostDecertificationTimelineSerializer(BaseTimelineSerializer):
    id = serializers.IntegerField()
    department = serializers.CharField(source="department.agency_name")
    allegations = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return POST_DECERTIFICATION_TIMELINE_KIND

    def get_allegations(self, obj):
        complaints = obj.complaints.all()

        return [
            complaint.allegation for complaint in complaints if complaint.allegation
        ]


class FirearmTimelineSerializer(BaseTimelineSerializer):
    def get_kind(self, obj):
        return FIREARM_CERTIFICATION_TIMELINE_KIND


class PC12QualificationTimelineSerializer(BaseTimelineSerializer):
    def get_kind(self, obj):
        return PC_12_QUALIFICATION_TIMELINE_KIND


class BradyTimelineSerializer(BaseTimelineSerializer):
    id = serializers.IntegerField()
    department = serializers.CharField(source="department.agency_name")
    allegation_desc = serializers.CharField()
    action = serializers.CharField()
    disposition = serializers.CharField()
    tracking_id_og = serializers.CharField()
    source_department = serializers.SerializerMethodField()
    charging_department = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()

    def _get_department_mappings(self):
        slugify_mappings = {
            department.agency_slug: department.agency_name
            for department in Department.objects.only("agency_name", "agency_slug")
        }

        return slugify_mappings

    def get_kind(self, obj):
        return BRADY_LIST_TIMELINE_KIND

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

    def get_source_department(self, obj):
        department_mappings = self._get_department_mappings()

        return department_mappings[obj.source_agency]

    def get_charging_department(self, obj):
        department_mappings = self._get_department_mappings()
        charging_department = department_mappings.get(obj.charging_agency)

        return charging_department if charging_department else None
