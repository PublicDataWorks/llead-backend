from rest_framework import serializers


class FrontPageOrderSerializer(serializers.Serializer):
    section = serializers.CharField()
    order = serializers.IntegerField()
