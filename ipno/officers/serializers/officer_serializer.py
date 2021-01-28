from rest_framework import serializers


class DepartmentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class OfficerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    badges = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()

    def get_badges(self, obj):
        return [
            officer_history.badge_no for officer_history in obj.officerhistory_set.all()
            if officer_history.badge_no
        ]

    def get_department(self, obj):
        officer_history = obj.officerhistory_set.first()
        if officer_history:
            return DepartmentSerializer(officer_history.department).data
