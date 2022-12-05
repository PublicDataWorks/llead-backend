from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from app_config.constants import CMS_KEY
from app_config.models import (
    AppTextContent,
    AppValueConfig,
    FrontPageCard,
    FrontPageOrder,
)
from app_config.serializers import FrontPageCardSerializer, FrontPageOrderSerializer
from utils.cache_utils import custom_cache


class AppConfigViewSet(ViewSet):
    @custom_cache
    def list(self, request):
        app_config = AppValueConfig.objects.all()
        app_text_contents = AppTextContent.objects.all()
        config_data = {}
        for config_object in app_config:
            config_data[config_object.name] = config_object.value
        cms_data = {}
        for app_text_content in app_text_contents:
            cms_data[app_text_content.name] = app_text_content.value

        config_data[CMS_KEY] = cms_data
        return Response(config_data)


class FrontPageOrdersViewSet(viewsets.ViewSet):
    @custom_cache
    def list(self, request):
        front_page_orders = FrontPageOrder.objects.all()

        serializer = FrontPageOrderSerializer(front_page_orders, many=True)
        return Response(serializer.data)


class FrontPageCardsViewSet(viewsets.ViewSet):
    @custom_cache
    def list(self, request):
        front_page_cards = FrontPageCard.objects.all()

        serializer = FrontPageCardSerializer(front_page_cards, many=True)
        return Response(serializer.data)
