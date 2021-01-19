from django.core.management.base import BaseCommand
from app_config.models import AppConfig, AppTextContent
from app_config.constants import APP_CONFIG, APP_TEXT_CONTENTS


class Command(BaseCommand):
    def handle(self, *args, **options):
        for config_data in APP_CONFIG:
            config_object = AppConfig.objects.filter(name=config_data['name']).first()
            if not config_object:
                AppConfig.objects.create(**config_data)

        for app_text_content_data in APP_TEXT_CONTENTS:
            app_text_content = AppTextContent.objects.filter(name=app_text_content_data['name']).first()
            if not app_text_content:
                AppTextContent.objects.create(**app_text_content_data)
