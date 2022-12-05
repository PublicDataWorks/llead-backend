from rest_framework import serializers


class DepartmentSerializer(serializers.Serializer):
    id = serializers.CharField(source="slug")
    name = serializers.CharField()
    city = serializers.CharField()
    parish = serializers.CharField()
    location_map_url = serializers.CharField()
