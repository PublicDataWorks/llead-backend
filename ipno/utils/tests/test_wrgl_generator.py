from unittest.mock import patch, Mock

from django.conf import settings
from django.test import TestCase

from news_articles.constants import NEWS_ARTICLE_WRGL_COLUMNS
from news_articles.factories import NewsArticleFactory
from news_articles.models import NewsArticle
from utils.wrgl_generator import WrglGenerator


class WrglGeneratorTestCase(TestCase):
    def setUp(self):
        self.wrgl_generator = WrglGenerator()

    @patch('utils.wrgl_generator.IO')
    @patch('utils.wrgl_generator.pd.DataFrame')
    def test_generate_csv_file(self, mock_pd_dataframe, mock_io):
        NewsArticleFactory()

        mock_getvalue = Mock()
        mock_getvalue.return_value = 'buffer'
        mock_close = Mock()
        mock_io_object = Mock(
            getvalue=mock_getvalue,
            close=mock_close
        )
        mock_io.return_value = mock_io_object

        mock_to_csv = Mock()
        mock_pd_dataframe.return_value = Mock(to_csv=mock_to_csv)

        news_objects = NewsArticle.objects.all()
        news_objects.values = Mock(return_value='data')
        result = self.wrgl_generator.generate_csv_file(news_objects, NEWS_ARTICLE_WRGL_COLUMNS)

        mock_io.assert_called()
        mock_pd_dataframe.assert_called_with('data')
        mock_to_csv.assert_called_with(mock_io_object, index=False, compression="gzip")
        mock_getvalue.assert_called()
        mock_close.assert_called()
        assert result == 'buffer'

    @patch('utils.wrgl_generator.requests.post')
    def test_create_wrgl_commit(self, mock_requests_post):
        mock_requests_post.return_value = 'response'

        url = f'https://www.wrgl.co/api/v1/users/{settings.WRGL_USER}/repos'

        data = {
            'repoName': 'test',
            'message': 'message',
            'csv.primaryKey': ['id'],
        }

        header = {
            'Authorization': f'APIKEY {settings.WRGL_API_KEY}',
        }

        result = self.wrgl_generator.create_wrgl_commit('test', 'message', ['id'], 'buffer')
        mock_requests_post.assert_called_with(url, data=data, headers=header, files={'csv.dataFile': 'buffer'})
        assert result == 'response'
