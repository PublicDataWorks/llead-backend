from django.core.management import call_command
from django.test import TestCase

from app_config.factories import AppConfigFactory, AppTextContentFactory, FrontPageOrderFactory
from app_config.models import AppConfig, AppTextContent, FrontPageOrder
from app_config.constants import APP_CONFIG, APP_TEXT_CONTENTS, APP_FRONT_PAGE_SECTIONS


class CreateInitialAppConfigCommandTestCase(TestCase):
    def test_call_command(self):
        call_command('create_initial_app_config')
        config_objects = AppConfig.objects.all()
        app_text_contents = AppTextContent.objects.all()
        app_sections = FrontPageOrder.objects.all()
        assert config_objects.count() == len(APP_CONFIG)
        assert app_text_contents.count() == len(APP_TEXT_CONTENTS)
        assert app_sections.count() == len(APP_FRONT_PAGE_SECTIONS)

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

        for app_section_data in APP_FRONT_PAGE_SECTIONS:
            app_section_object = app_sections.filter(section=app_section_data).first()
            assert app_section_object
            assert app_section_object.section == app_section_data

    def test_call_command_with_partial_created_data(self):
        create_app_config = APP_CONFIG[0]
        create_app_text_content = APP_TEXT_CONTENTS[0]
        create_app_section = APP_FRONT_PAGE_SECTIONS[0]
        AppConfigFactory(
            name=create_app_config['name'],
            value=create_app_config['value'],
            description=create_app_config['description']
        )
        AppTextContentFactory(
            name=create_app_text_content['name'],
            value=create_app_text_content['value'],
            description=create_app_text_content['description']
        )
        FrontPageOrderFactory(
            section=create_app_section
        )
        assert AppConfig.objects.all().count() == 1
        assert AppTextContent.objects.all().count() == 1
        assert FrontPageOrder.objects.all().count() == 1

        call_command('create_initial_app_config')
        config_objects = AppConfig.objects.all()
        app_text_contents = AppTextContent.objects.all()
        app_sections = FrontPageOrder.objects.all()
        assert config_objects.count() == len(APP_CONFIG)
        assert app_text_contents.count() == len(APP_TEXT_CONTENTS)
        assert app_sections.count() == len(APP_FRONT_PAGE_SECTIONS)

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

        for app_section_data in APP_FRONT_PAGE_SECTIONS:
            app_section_object = app_sections.filter(section=app_section_data).first()
            assert app_section_object
            assert app_section_object.section == app_section_data
