from unittest.mock import call, patch

from django.core.management import call_command
from django.test import TestCase


class CreateInitialAppConfigDataTestCase(TestCase):
    @patch("core.management.commands.init_project_config.call_command")
    def test_call_commands(self, mock_call_command):
        call_command("init_project_config")

        expected_calls = [
            call("create_initial_app_config"),
            call("create_initial_wrgl_repos"),
            call("create_initial_news_articles_sources"),
            call("create_initial_tasks"),
        ]

        mock_call_command.assert_has_calls(expected_calls)
