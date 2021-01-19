from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from app_config.models import AppConfig, AppTextContent
from app_config.constants import CMS_KEY


class AppConfigViewSet(ViewSet):
    def list(self, request):
        app_config = AppConfig.objects.all()
        app_text_contents = AppTextContent.objects.all()
        config_data = {}
        for config_object in app_config:
            config_data[config_object.name] = config_object.value
        cms_data = {}
        for app_text_content in app_text_contents:
            cms_data[app_text_content.name] = app_text_content.value

        config_data[CMS_KEY] = cms_data
        return Response(config_data)
