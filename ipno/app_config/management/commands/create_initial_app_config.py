from django.core.management.base import BaseCommand

from app_config.constants import APP_CONFIG, APP_FRONT_PAGE_SECTIONS, APP_TEXT_CONTENTS
from app_config.models import AppTextContent, AppValueConfig, FrontPageOrder


class Command(BaseCommand):
    def handle(self, *args, **options):
        for config_data in APP_CONFIG:
            config_object = AppValueConfig.objects.filter(
                name=config_data["name"]
            ).first()
            if not config_object:
                AppValueConfig.objects.create(**config_data)

        for app_text_content_data in APP_TEXT_CONTENTS:
            app_text_content = AppTextContent.objects.filter(
                name=app_text_content_data["name"]
            ).first()
            if not app_text_content:
                AppTextContent.objects.create(**app_text_content_data)

        for app_section in APP_FRONT_PAGE_SECTIONS:
            app_section_order = FrontPageOrder.objects.filter(
                section=app_section
            ).first()
            if not app_section_order:
                FrontPageOrder.objects.create(section=app_section)
