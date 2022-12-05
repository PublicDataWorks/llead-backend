from django.test.testcases import TestCase

from mock import patch

from app_config.factories import (
    AppTextContentFactory,
    AppValueConfigFactory,
    FrontPageCardFactory,
    FrontPageOrderFactory,
)


class AppConfigTestCase(TestCase):
    @patch("app_config.signals.delete_cache")
    def test_delete_app_config_cache_when_AppValueConfig_is_saved(
        self, mock_delete_cache
    ):
        app_value_config = AppValueConfigFactory()
        app_value_config.value = "test"
        app_value_config.save()

        mock_delete_cache.assert_called_with("api:app-config-list")

    @patch("app_config.signals.delete_cache")
    def test_delete_app_config_cache_when_AppTextContent_is_saved(
        self, mock_delete_cache
    ):
        app_text_content = AppTextContentFactory()
        app_text_content.value = "test"
        app_text_content.save()

        mock_delete_cache.assert_called_with("api:app-config-list")

    @patch("app_config.signals.delete_cache")
    def test_delete_front_page_card_cache_when_FrontPageCard_is_saved(
        self, mock_delete_cache
    ):
        front_page_card = FrontPageCardFactory()
        front_page_card.value = "test"
        front_page_card.save()

        mock_delete_cache.assert_called_with("api:front-page-cards-list")

    @patch("app_config.signals.delete_cache")
    def test_delete_front_page_card_cache_when_FrontPageOrder_is_saved(
        self, mock_delete_cache
    ):
        front_page_order = FrontPageOrderFactory()
        front_page_order.content = "test"
        front_page_order.save()

        mock_delete_cache.assert_called_with("api:front-page-orders-list")
