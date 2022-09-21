import datetime
from unittest.mock import patch

from django.urls import reverse

from rest_framework import status

from news_articles.factories import NewsArticleFactory, NewsArticleSourceFactory
from news_articles.factories.matched_sentence_factory import MatchedSentenceFactory
from officers.factories import OfficerFactory
from test_utils.auth_api_test_case import AuthAPITestCase


class NewsArticlesViewSetTestCase(AuthAPITestCase):
    def test_list_success(self):
        source = NewsArticleSourceFactory(source_display_name='dummy')
        officer = OfficerFactory()
        news_article_1 = NewsArticleFactory(source=source)
        news_article_2 = NewsArticleFactory(
            source=source,
            published_date=news_article_1.published_date - datetime.timedelta(days=1)
        )
        news_article_3 = NewsArticleFactory(
            source=source,
            is_hidden=True,
        )
        matched_sentence_1 = MatchedSentenceFactory(article=news_article_1)
        matched_sentence_2 = MatchedSentenceFactory(article=news_article_2)
        matched_sentence_3 = MatchedSentenceFactory(article=news_article_3)
        NewsArticleFactory()
        matched_sentence_1.officers.add(officer)
        matched_sentence_1.save()
        matched_sentence_2.officers.add(officer)
        matched_sentence_2.save()
        matched_sentence_3.officers.add(officer)
        matched_sentence_3.save()

        response = self.client.get(reverse('api:news-articles-list'))
        assert response.status_code == status.HTTP_200_OK

        expected_data = [
            {
                'id': news_article_1.id,
                'date': str(news_article_1.published_date),
                'title': news_article_1.title,
                'url': news_article_1.url,
                'source_name': source.source_display_name,
                'author': news_article_1.author,
            },
            {
                'id': news_article_2.id,
                'date': str(news_article_2.published_date),
                'title': news_article_2.title,
                'url': news_article_2.url,
                'source_name': source.source_display_name,
                'author': news_article_2.author,
            },
        ]

        assert response.data == expected_data

    @patch('news_articles.views.flush_news_article_related_caches')
    def test_hide_success(self, mock_flush_news_article_related_caches):
        NewsArticleFactory(id=1)
        NewsArticleFactory(id=2)
        NewsArticleFactory(id=3)

        response = self.admin_client.post(reverse('api:news-articles-hide', kwargs={'pk': 1}))

        mock_flush_news_article_related_caches.assert_called()

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'detail': 'the news articles is hidden'
        }

    def test_hide_unauthorized(self):
        response = self.client.post(reverse('api:news-articles-hide', kwargs={'pk': 1}))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_hide_with_non_admin(self):
        response = self.auth_client.post(reverse('api:news-articles-hide', kwargs={'pk': 1}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_hide_not_found(self):
        response = self.admin_client.post(reverse('api:news-articles-hide', kwargs={'pk': 1}))
        assert response.status_code == status.HTTP_404_NOT_FOUND
