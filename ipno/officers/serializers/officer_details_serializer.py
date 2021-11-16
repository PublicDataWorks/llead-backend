from django.db.models import F

from rest_framework import serializers

from departments.models import Department
from officers.models import Event
from shared.serializers import SimpleDepartmentSerializer


class OfficerDetailsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    badges = serializers.SerializerMethodField()
    birth_year = serializers.IntegerField()
    race = serializers.CharField()
    gender = serializers.CharField()

    departments = serializers.SerializerMethodField()
    salary = serializers.SerializerMethodField()
    salary_freq = serializers.SerializerMethodField()
    documents_count = serializers.SerializerMethodField()
    complaints_count = serializers.SerializerMethodField()

    def _get_latest_salary_event(self, obj):
        if not hasattr(obj, 'latest_salary_event'):
            setattr(
                obj,
                'latest_salary_event',
                obj.events.filter(
                    salary__isnull=False,
                    salary_freq__isnull=False,
                ).order_by(
                    '-year', '-month', '-day'
                ).first()
            )
        return obj.latest_salary_event

    def get_badges(self, obj):
        all_officers = obj.person.officers.all()
        events_qs = Event.objects.filter(officer__in=all_officers).order_by(
            F('year').desc(nulls_last=True),
            F('month').desc(nulls_last=True),
            F('day').desc(nulls_last=True),
        ).filter(
            badge_no__isnull=False
        ).values_list('badge_no', flat=True)
        events = list(dict.fromkeys(events_qs))
        return events

    def get_departments(self, obj):
        all_officers = obj.person.officers.all()
        departments = Department.objects.filter(officers__in=all_officers).distinct()
        return SimpleDepartmentSerializer(departments, many=True).data

    def get_salary(self, obj):
        event = self._get_latest_salary_event(obj)
        salary_field = serializers.DecimalField(max_digits=8, decimal_places=2)
        return salary_field.to_representation(event.salary) if event else None

    def get_salary_freq(self, obj):
        event = self._get_latest_salary_event(obj)
        return event.salary_freq if event else None

    def get_documents_count(self, obj):
        return obj.documents.count()

    def get_complaints_count(self, obj):
        return obj.complaints.count()
