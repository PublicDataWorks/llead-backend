from unittest.mock import patch

from django.test import TestCase

from news_articles.management.commands.run_news_articles_officers_matching import Command


class CommandTestCase(TestCase):
    def setUp(self):
        self.command = Command()

    @patch('news_articles.management.commands.run_news_articles_officers_matching.ProcessMatchingArticle.process')
    @patch('news_articles.management.commands.run_news_articles_officers_matching.ProcessExcludeArticleOfficer.process')
    @patch('news_articles.management.commands.run_news_articles_officers_matching.rebuild_search_index')
    @patch('news_articles.management.commands.run_news_articles_officers_matching.flush_news_article_related_caches')
    def test_handle(
            self,
            mock_flush_news_article_related_caches,
            mock_rebuild_search_index,
            mock_matching_keywords_process,
            mock_process_exclude_article_officer,
    ):
        mock_matching_keywords_process.return_value = True
        mock_process_exclude_article_officer.return_value = True

        self.command.handle()

        mock_matching_keywords_process.assert_called()
        mock_process_exclude_article_officer.assert_called()
        mock_rebuild_search_index.assert_called()
        mock_flush_news_article_related_caches.assert_called()

    @patch('news_articles.management.commands.run_news_articles_officers_matching.ProcessMatchingArticle.process')
    @patch('news_articles.management.commands.run_news_articles_officers_matching.ProcessExcludeArticleOfficer.process')
    @patch('news_articles.management.commands.run_news_articles_officers_matching.rebuild_search_index')
    @patch('news_articles.management.commands.run_news_articles_officers_matching.flush_news_article_related_caches')
    def test_handle_not_rebuild_index_and_flush_cache(
            self,
            mock_flush_news_article_related_caches,
            mock_rebuild_search_index,
            mock_matching_keywords_process,
            mock_process_exclude_article_officer,
    ):
        mock_matching_keywords_process.return_value = False
        mock_process_exclude_article_officer.return_value = False

        self.command.handle()

        mock_matching_keywords_process.assert_called()
        mock_process_exclude_article_officer.assert_called()
        mock_rebuild_search_index.assert_not_called()
        mock_flush_news_article_related_caches.assert_not_called()
