from datetime import datetime
from unittest.mock import MagicMock, call

from django.conf import settings
from django.core.management import call_command
from django.test.testcases import TestCase
from django.utils.text import slugify

import pytz
from mock import patch

from news_articles.factories import NewsArticleFactory, NewsArticleSourceFactory


class FixInvalidNewsArticlesTestCase(TestCase):
    @patch(
        "news_articles.management.commands.fix_invalid_news_articles.NEWS_ARTICLE_CLOUD_SPACES",
        "news_articles",
    )
    @patch(
        "news_articles.management.commands.fix_invalid_news_articles.GoogleCloudService"
    )
    def test_call_command(self, mock_google_cloud_service):
        mock_gcs_return = MagicMock()
        mock_google_cloud_service.return_value = mock_gcs_return
        source = NewsArticleSourceFactory(source_name="source")
        url_1 = f"{settings.GC_PATH}news_articles/{source.source_name}/2020-04-05_http://guid-1.pdf"
        article_1 = NewsArticleFactory(
            guid="http://guid-1",
            url=url_1,
            title="article_1",
            published_date=datetime(2020, 4, 5, tzinfo=pytz.utc),
            source=source,
        )
        url_2 = f"{settings.GC_PATH}news_articles/{source.source_name}/2020-04-05_http://other.com?guid=2.pdf"
        article_2 = NewsArticleFactory(
            guid="http://other.com?guid=2",
            url=url_2,
            source=source,
            title="news_2",
            published_date=datetime(2020, 4, 5, tzinfo=pytz.utc),
        )

        mock_gcs_return.is_object_exists.return_value = True

        call_command("fix_invalid_news_articles")

        old_file_path_1 = (
            f"news_articles/{source.source_name}/2020-04-05_{article_1.guid}.pdf"
        )
        old_file_path_2 = (
            f"news_articles/{source.source_name}/2020-04-05_{article_2.guid}.pdf"
        )

        mock_gcs_return.is_object_exists.assert_has_calls(
            [call(old_file_path_1), call(old_file_path_2)]
        )

        new_file_path_1 = f"news_articles/{source.source_name}/2020-04-05_{slugify(article_1.title)}.pdf"
        new_file_path_2 = f"news_articles/{source.source_name}/2020-04-05_{slugify(article_2.title)}.pdf"
        mock_gcs_return.move_blob_internally.assert_has_calls(
            [
                call(old_file_path_1, new_file_path_1),
                call(old_file_path_2, new_file_path_2),
            ]
        )

        article_1.refresh_from_db()
        article_2.refresh_from_db()

        assert article_1.url == f"{settings.GC_PATH}{new_file_path_1}"
        assert article_2.url == f"{settings.GC_PATH}{new_file_path_2}"

    @patch(
        "news_articles.management.commands.fix_invalid_news_articles.NEWS_ARTICLE_CLOUD_SPACES",
        "news_articles",
    )
    @patch(
        "news_articles.management.commands.fix_invalid_news_articles.GoogleCloudService"
    )
    def test_object_not_exists(self, mock_google_cloud_service):
        mock_gcs_return = MagicMock()
        mock_google_cloud_service.return_value = mock_gcs_return
        source = NewsArticleSourceFactory(source_name="source")
        url_1 = f"{settings.GC_PATH}news_articles/{source.source_name}/2020-04-05_http://guid-1.pdf"
        article_1 = NewsArticleFactory(
            guid="http://guid-1",
            url=url_1,
            title="article_1",
            published_date=datetime(2020, 4, 5, tzinfo=pytz.utc),
            source=source,
        )
        url_2 = f"{settings.GC_PATH}news_articles/{source.source_name}/2020-04-05_http://other.com?guid=2.pdf"
        NewsArticleFactory(
            guid="http://other.com?guid=2",
            url=url_2,
            source=source,
            title="news_2",
            published_date=datetime(2020, 4, 5, tzinfo=pytz.utc),
        )

        mock_gcs_return.is_object_exists.return_value = False

        call_command("fix_invalid_news_articles")

        old_file_path_1 = (
            f"news_articles/{source.source_name}/2020-04-05_{article_1.guid}.pdf"
        )
        mock_gcs_return.is_object_exists.assert_has_calls(
            [
                call(old_file_path_1),
            ]
        )

        mock_gcs_return.move_blob_internally.assert_not_called()
