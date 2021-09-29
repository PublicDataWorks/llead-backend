import sys
from unittest.mock import patch

from django.test import TestCase

from app_config.apps import AppConfig
from app_config.models import FrontPageOrder


class AppsTestCase(TestCase):
    def setUp(self):
        self.app_config = AppConfig('app_config', sys.modules[__name__])

    @patch('tasks.apps.connection.introspection.table_names')
    def test_on_app_ready(self, mock_table_names):
        mock_table_names.return_value = ['app_config_frontpageorder']

        self.app_config.on_app_ready()

        items = FrontPageOrder.objects.all()

        assert items.count() == 4

        assert items.first().section == 'DEPARTMENT'
        assert items.first().order == 1

        assert items.last().section == 'DOCUMENT'
        assert items.last().order == 4

    @patch('tasks.apps.connection.introspection.table_names')
    def test_not_init_table(self, mock_table_names):
        mock_table_names.return_value = []

        self.app_config.on_app_ready()

        items = FrontPageOrder.objects.all()

        assert items.count() == 0
