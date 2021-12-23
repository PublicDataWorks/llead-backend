from rest_framework import serializers


class DepartmentOfficerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    is_starred = serializers.BooleanField()
    use_of_forces_count = serializers.IntegerField()

    badges = serializers.SerializerMethodField()
    complaints_count = serializers.SerializerMethodField()

    def get_badges(self, obj):
        all_officers = obj.person.officers.all()

        events = list(dict.fromkeys([
            event.badge_no for officer in all_officers for event in officer.events.all()
            if event.badge_no
        ]))

        return events

    def get_complaints_count(self, obj):
        return obj.person.all_complaints_count
