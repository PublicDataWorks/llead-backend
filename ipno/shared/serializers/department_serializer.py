from rest_framework import serializers


class DepartmentSerializer(serializers.Serializer):
    id = serializers.CharField(source="agency_slug")
    name = serializers.CharField(source="agency_name")
    city = serializers.CharField()
    parish = serializers.CharField()
    location_map_url = serializers.CharField()
