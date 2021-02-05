from rest_framework import serializers

from shared.serializers import BaseDocumentSerializer


class DocumentSerializer(BaseDocumentSerializer):
    preview_image_url = serializers.CharField()
    pages_count = serializers.IntegerField()
