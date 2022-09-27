from django.apps import AppConfig


class SiteAppConfig(AppConfig):
    name = 'app_config'

    def ready(self):
        import app_config.signals # noqa
