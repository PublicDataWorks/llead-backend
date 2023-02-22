from rest_framework import serializers


class DepartmentCoordinateSerializer(serializers.Serializer):
    id = serializers.CharField(source="agency_slug")
    name = serializers.CharField(source="agency_name")
    location = serializers.SerializerMethodField()

    def get_location(self, obj):
        return obj.location
