from rest_framework import serializers

from departments.models import Department
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
    latest_rank = serializers.SerializerMethodField()

    def _get_person_officers(self, obj):
        if not hasattr(obj, 'person_officers'):
            person_officers = obj.person.officers.all()
            setattr(
                obj,
                'person_officers',
                person_officers
            )

        return obj.person_officers

    def _get_all_events(self, obj):
        if not hasattr(obj, 'all_events'):
            all_officers = self._get_person_officers(obj)

            all_events = []
            for officer in all_officers:
                all_events.extend(officer.events.all())

            all_events.sort(key=lambda k: (
                (k.year is None, -k.year if k.year is not None else None),
                (k.month is None, -k.month if k.month is not None else None),
                (k.day is None, -k.day if k.day is not None else None)
            ))

            setattr(
                obj,
                'all_events',
                all_events
            )

        return obj.all_events

    def _get_first_salary_event(self, obj):
        if not hasattr(obj, 'first_salary_event'):
            all_events = self._get_all_events(obj)

            first_salary_event = None
            for event in all_events:
                if event.salary and event.salary_freq:
                    first_salary_event = event
                    break

            setattr(
                obj,
                'first_salary_event',
                first_salary_event
            )

        return obj.first_salary_event

    def get_badges(self, obj):
        all_events = self._get_all_events(obj)

        events = list(dict.fromkeys([
            event.badge_no for event in all_events if event.badge_no
        ]))
        return events

    def get_departments(self, obj):
        all_officers = self._get_person_officers(obj)
        departments = Department.objects.filter(officers__in=all_officers).distinct()
        return SimpleDepartmentSerializer(departments, many=True).data

    def get_salary(self, obj):
        salary_event = self._get_first_salary_event(obj)
        salary_field = serializers.DecimalField(max_digits=8, decimal_places=2)
        return salary_field.to_representation(salary_event.salary) if salary_event else None

    def get_salary_freq(self, obj):
        salary_event = self._get_first_salary_event(obj)
        return salary_event.salary_freq if salary_event else None

    def get_documents_count(self, obj):
        return obj.documents.count()

    def get_complaints_count(self, obj):
        return obj.complaints.count()

    def get_latest_rank(self, obj):
        events = self._get_all_events(obj)

        rank_events = [rank for rank in events if rank.rank_desc]

        return rank_events[0].rank_desc if rank_events else None
