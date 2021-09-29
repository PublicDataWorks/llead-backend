from unittest.mock import patch

from django.test import TestCase

from news_articles.management.commands.run_news_articles_officers_matching import Command


class CommandTestCase(TestCase):
    def setUp(self):
        self.command = Command()

    @patch('news_articles.management.commands.run_news_articles_officers_matching.ProcessMatchingArticle.process')
    def test_handle(self, mock_matching_keywords_process):
        self.command.handle()

        mock_matching_keywords_process.assert_called()
