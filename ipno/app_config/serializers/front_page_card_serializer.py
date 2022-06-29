from rest_framework import serializers


class FrontPageCardSerializer(serializers.Serializer):
    content = serializers.CharField()
