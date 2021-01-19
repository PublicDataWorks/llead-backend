from django.core.management import call_command
from django.test import TestCase

from app_config.models import AppConfig, AppTextContent
from app_config.constants import APP_CONFIG, APP_TEXT_CONTENTS


class CreateInitialAppConfigCommandTestCase(TestCase):
    def test_call_command(self):
        call_command('create_initial_app_config')
        config_objects = AppConfig.objects.all()
        app_text_contents = AppTextContent.objects.all()
        assert config_objects.count() == len(APP_CONFIG)
        assert app_text_contents.count() == len(APP_TEXT_CONTENTS)

        for config_data in APP_CONFIG:
            config_object = config_objects.filter(name=config_data['name']).first()
            assert config_object
            assert config_object.name == config_data['name']
            assert config_object.value == config_data['value']
            assert config_object.description == config_data['description']

        for app_text_content_data in APP_TEXT_CONTENTS:
            app_text_content = app_text_contents.filter(name=app_text_content_data['name']).first()
            assert app_text_content
            assert app_text_content.name == app_text_content_data['name']
            assert app_text_content.value == app_text_content_data['value']
            assert app_text_content.description == app_text_content_data['description']
