from rest_framework import serializers


class SimpleDepartmentSerializer(serializers.Serializer):
    id = serializers.CharField(source='slug')
    name = serializers.CharField()
