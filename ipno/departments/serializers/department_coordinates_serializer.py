from rest_framework import serializers


class DepartmentCoordinateSerializer(serializers.Serializer):
    id = serializers.CharField(source='slug')
    name = serializers.CharField()
    location = serializers.SerializerMethodField()

    def get_location(self, obj):
        return obj.location
