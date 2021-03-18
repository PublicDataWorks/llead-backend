from rest_framework import serializers

from shared.serializers import SimpleDepartmentSerializer
from utils.data_utils import data_period


class OfficerDetailsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    badges = serializers.ListField(child=serializers.CharField())
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

    def get_department(self, obj):
        officer_history = obj.officerhistory_set.order_by('-start_date').first()
        if officer_history:
            return SimpleDepartmentSerializer(officer_history.department).data

    def get_annual_salary(self, obj):
        officer_history = obj.officerhistory_set.order_by('-start_date').first()
        return officer_history.annual_salary if officer_history else None

    def get_documents_count(self, obj):
        return obj.document_set.count()

    def get_complaints_count(self, obj):
        return obj.complaint_set.count()

    def get_data_period(self, obj):
        officer_history_periods = list(obj.officerhistory_set.filter(
            start_date__isnull=False,
            end_date__isnull=False
        ).order_by('start_date__year').values_list('start_date__year', 'end_date__year'))

        years = obj.document_years + obj.complaint_years
        return data_period(officer_history_periods, years)

    def get_documents_data_period(self, obj):
        return data_period([], obj.document_years)

    def get_complaints_data_period(self, obj):
        return data_period([], obj.complaint_years)
