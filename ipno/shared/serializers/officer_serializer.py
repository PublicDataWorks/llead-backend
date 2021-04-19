from rest_framework import serializers

from shared.serializers import SimpleDepartmentSerializer


class OfficerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    badges = serializers.ListField(child=serializers.CharField())
    department = serializers.SerializerMethodField()

    def get_department(self, obj):
        event = obj.event_set.first()
        if event:
            return SimpleDepartmentSerializer(event.department).data
