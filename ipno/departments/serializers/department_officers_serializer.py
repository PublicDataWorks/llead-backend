from rest_framework import serializers

from departments.models import Department
from shared.serializers import SimpleDepartmentSerializer


class DepartmentOfficerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    is_starred = serializers.BooleanField(default=False)
    use_of_forces_count = serializers.IntegerField()

    badges = serializers.SerializerMethodField()
    complaints_count = serializers.SerializerMethodField()
    departments = serializers.SerializerMethodField()

    def get_badges(self, obj):
        all_officers = obj.person.officers.all()

        events = list(dict.fromkeys([
            event.badge_no for officer in all_officers for event in officer.events.all()
            if event.badge_no
        ]))

        return events

    def get_complaints_count(self, obj):
        return obj.person.all_complaints_count

    def get_departments(self, obj):
        departments = Department.objects.filter(officers=obj).distinct()
        return SimpleDepartmentSerializer(departments, many=True).data
