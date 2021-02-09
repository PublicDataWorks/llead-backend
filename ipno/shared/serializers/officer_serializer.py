from rest_framework import serializers

from shared.serializers import SimpleDepartmentSerializer


class OfficerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    badges = serializers.ListField(child=serializers.CharField())
    department = serializers.SerializerMethodField()

    def get_department(self, obj):
        officer_history = obj.officerhistory_set.first()
        if officer_history:
            return SimpleDepartmentSerializer(officer_history.department).data
