from django.apps import AppConfig
from django.db import connection

from app_config.constants import APP_FRONT_PAGE_SECTIONS


class AppConfig(AppConfig):
    name = 'app_config'

    def ready(self):
        self.on_app_ready() # noqa

    def on_app_ready(self):
        if "app_config_frontpageorder" in connection.introspection.table_names():
            from app_config.models import FrontPageOrder
            all_sections = FrontPageOrder.objects.all().values_list('section', flat=True)

            for app_section in APP_FRONT_PAGE_SECTIONS:
                if app_section not in all_sections:
                    FrontPageOrder.objects.create(section=app_section)
