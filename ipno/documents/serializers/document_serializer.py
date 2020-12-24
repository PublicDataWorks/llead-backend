from rest_framework import serializers


class DocumentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
