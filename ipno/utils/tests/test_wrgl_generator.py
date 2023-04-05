from unittest.mock import MagicMock, Mock, patch

from django.test import TestCase, override_settings

from news_articles.constants import NEWS_ARTICLE_WRGL_COLUMNS
from news_articles.factories import NewsArticleFactory
from news_articles.models import NewsArticle
from utils.wrgl_generator import WrglGenerator


class WrglGeneratorTestCase(TestCase):
    def setUp(self):
        self.wrgl_generator = WrglGenerator()

    @patch("utils.wrgl_generator.IO")
    @patch("utils.wrgl_generator.pd.DataFrame")
    def test_generate_csv_file(self, mock_pd_dataframe, mock_io):
        NewsArticleFactory()

        mock_getvalue = Mock()
        mock_getvalue.return_value = "buffer"
        mock_close = Mock()
        mock_io_object = Mock(getvalue=mock_getvalue, close=mock_close)
        mock_io.return_value = mock_io_object

        mock_to_csv = Mock()
        mock_pd_dataframe.return_value = Mock(to_csv=mock_to_csv)

        news_objects = NewsArticle.objects.all()
        news_objects.values = Mock(return_value="data")
        result = self.wrgl_generator.generate_csv_file(
            news_objects, NEWS_ARTICLE_WRGL_COLUMNS
        )

        mock_io.assert_called()
        mock_pd_dataframe.assert_called_with("data")
        mock_to_csv.assert_called_with(mock_io_object, index=False)
        mock_getvalue.assert_called()
        mock_close.assert_called()
        assert result == "buffer"

    @override_settings(WRGL_CLIENT_ID="test-id")
    @override_settings(WRGL_CLIENT_SECRET="test-secret")
    @patch("utils.wrgl_generator.Repository")
    def test_create_wrgl_commit(self, mock_Repository):
        mock_repo = MagicMock()
        mock_repo.commit.return_value = "response"
        mock_Repository.return_value = mock_repo

        result = self.wrgl_generator.create_wrgl_commit(
            "message", ["id"], b"buffer", "test-branch"
        )

        mock_Repository.assert_called_with(
            "https://wrgl.llead.co/",
            "test-id",
            "test-secret",
        )
        assert mock_repo.commit.call_args[1].get("branch") == "test-branch"
        assert mock_repo.commit.call_args[1].get("message") == "message"
        assert mock_repo.commit.call_args[1].get("primary_key") == ["id"]
        assert result == "response"
