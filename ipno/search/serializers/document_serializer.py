from rest_framework import serializers

from shared.serializers import BaseDocumentSerializer


class DocumentSerializer(BaseDocumentSerializer):
    text_content = serializers.CharField()
