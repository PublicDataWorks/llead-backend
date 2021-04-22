from django.db.models import F

from rest_framework import serializers

from shared.serializers import SimpleDepartmentSerializer
from utils.data_utils import data_period
from officers.constants import COMPLAINT_EVENT_KINDS


class OfficerDetailsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    badges = serializers.SerializerMethodField()
    birth_year = serializers.IntegerField()
    race = serializers.CharField()
    gender = serializers.CharField()

    department = serializers.SerializerMethodField()
    annual_salary = serializers.SerializerMethodField()
    documents_count = serializers.SerializerMethodField()
    complaints_count = serializers.SerializerMethodField()
    data_period = serializers.SerializerMethodField()
    documents_data_period = serializers.SerializerMethodField()
    complaints_data_period = serializers.SerializerMethodField()

    def get_badges(self, obj):
        return list(obj.event_set.order_by(
            F('year').desc(nulls_last=True),
            F('month').desc(nulls_last=True),
            F('day').desc(nulls_last=True),
        ).filter(
            badge_no__isnull=False
        ).values_list('badge_no', flat=True))

    def get_department(self, obj):
        event = obj.event_set.order_by('-year', '-month', '-day').first()
        if event:
            return SimpleDepartmentSerializer(event.department).data

    def get_annual_salary(self, obj):
        event = obj.event_set.filter(
            annual_salary__isnull=False
        ).order_by(
            '-year', '-month', '-day'
        ).first()
        return event.annual_salary if event else None

    def get_documents_count(self, obj):
        return obj.document_set.count()

    def get_complaints_count(self, obj):
        return obj.complaint_set.count()

    def get_data_period(self, obj):
        event_years = list(obj.event_set.filter(
            year__isnull=False,
        ).values_list('year', flat=True))

        years = event_years + obj.document_years
        return data_period(years)

    def get_documents_data_period(self, obj):
        return data_period(obj.document_years)

    def get_complaints_data_period(self, obj):
        complaint_years = list(obj.event_set.filter(
            year__isnull=False,
            kind__in=COMPLAINT_EVENT_KINDS
        ).values_list('year', flat=True))
        return data_period(complaint_years)
