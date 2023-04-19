from rest_framework import serializers


class FindingSerializer(serializers.Serializer):
    background_image_url = serializers.SerializerMethodField()
    title = serializers.CharField()
    description = serializers.CharField()
    card_image_url = serializers.SerializerMethodField()
    card_title = serializers.CharField()
    card_author = serializers.CharField()
    card_department = serializers.CharField()

    def get_background_image_url(self, obj):
        request = self.context.get("request")

        return (
            request.build_absolute_uri(obj.background_image.url)
            if obj.background_image
            else None
        )

    def get_card_image_url(self, obj):
        request = self.context.get("request")

        return (
            request.build_absolute_uri(obj.card_image.url)
            if obj.background_image
            else None
        )
