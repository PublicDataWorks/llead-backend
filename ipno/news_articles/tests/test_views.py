import datetime

from django.urls import reverse

from rest_framework import status

from news_articles.factories import NewsArticleFactory, NewsArticleSourceFactory
from officers.factories import OfficerFactory
from test_utils.auth_api_test_case import AuthAPITestCase


class NewsArticlesViewSetTestCase(AuthAPITestCase):
    def test_list_success(self):
        source = NewsArticleSourceFactory()
        officer = OfficerFactory()
        news_article_1 = NewsArticleFactory(source=source)
        news_article_2 = NewsArticleFactory(
            source=source,
            published_date=news_article_1.published_date - datetime.timedelta(days=1)
        )
        NewsArticleFactory()
        news_article_1.officers.add(officer)
        news_article_1.save()
        news_article_2.officers.add(officer)
        news_article_2.save()

        response = self.auth_client.get(reverse('api:news-articles-list'))
        assert response.status_code == status.HTTP_200_OK

        expected_data = [
            {
                'id': news_article_1.id,
                'date': str(news_article_1.published_date),
                'title': news_article_1.title,
                'url': news_article_1.url,
                'source_name': source.custom_matching_name,
            },
            {
                'id': news_article_2.id,
                'date': str(news_article_2.published_date),
                'title': news_article_2.title,
                'url': news_article_2.url,
                'source_name': source.custom_matching_name,
            },
        ]

        assert response.data == expected_data

    def test_list_unauthorized(self):
        response = self.client.get(reverse('api:news-articles-list'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
