from rest_framework import serializers

from shared.serializers import SimpleDepartmentSerializer


class OfficerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    badges = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()

    def get_badges(self, obj):
        all_officers = obj.person.officers.all()

        events = list(dict.fromkeys([
            event.badge_no for officer in all_officers for event in officer.events.all()
            if event.badge_no
        ]))

        return events

    def get_department(self, obj):
        event = obj.events.first()
        if event:
            return SimpleDepartmentSerializer(event.department).data
