from rest_framework import serializers


class SimpleDepartmentSerializer(serializers.Serializer):
    id = serializers.CharField(source="agency_slug")
    name = serializers.CharField(source="agency_name")
