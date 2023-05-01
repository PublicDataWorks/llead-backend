import datetime
from unittest.mock import patch

from django.urls import reverse

from rest_framework import status

from app_config.constants import APP_CONFIG
from app_config.factories import AppValueConfigFactory
from news_articles.documents import NewsArticleESDoc
from news_articles.factories import NewsArticleFactory, NewsArticleSourceFactory
from news_articles.factories.matched_sentence_factory import MatchedSentenceFactory
from news_articles.factories.news_article_classification_factory import (
    NewsArticleClassificationFactory,
)
from officers.factories import OfficerFactory
from test_utils.auth_api_test_case import AuthAPITestCase
from utils.search_index import rebuild_search_index


class NewsArticlesViewSetTestCase(AuthAPITestCase):
    def test_list_success(self):
        create_app_config = APP_CONFIG[2]

        AppValueConfigFactory(
            name=create_app_config["name"],
            value=create_app_config["value"],
            description=create_app_config["description"],
        )

        source = NewsArticleSourceFactory(source_display_name="dummy")
        officer = OfficerFactory()
        news_article_1 = NewsArticleFactory(source=source)
        news_article_2 = NewsArticleFactory(
            source=source,
            published_date=news_article_1.published_date - datetime.timedelta(days=1),
        )
        news_article_3 = NewsArticleFactory(
            source=source,
            is_hidden=True,
        )
        news_article_4 = NewsArticleFactory(source=source)
        news_article_5 = NewsArticleFactory(source=source)
        NewsArticleFactory()

        matched_sentence_1 = MatchedSentenceFactory(article=news_article_1)
        matched_sentence_2 = MatchedSentenceFactory(article=news_article_2)
        matched_sentence_3 = MatchedSentenceFactory(article=news_article_3)
        matched_sentence_4 = MatchedSentenceFactory(article=news_article_4)
        matched_sentence_5 = MatchedSentenceFactory(article=news_article_5)
        matched_sentence_1.officers.add(officer)
        matched_sentence_1.save()
        matched_sentence_2.officers.add(officer)
        matched_sentence_2.save()
        matched_sentence_3.officers.add(officer)
        matched_sentence_3.save()
        matched_sentence_4.officers.add(officer)
        matched_sentence_4.save()
        matched_sentence_5.officers.add(officer)
        matched_sentence_5.save()

        NewsArticleClassificationFactory(
            article_id=news_article_2.id,
            news_article=news_article_2,
            score=0.8,
            relevant="relevant",
        )
        NewsArticleClassificationFactory(
            article_id=news_article_4.id,
            news_article=news_article_4,
            score=0.4,
            relevant="relevant",
        )
        NewsArticleClassificationFactory(
            article_id=news_article_5.id,
            news_article=news_article_5,
            score=0.3,
            relevant="not_relevant",
        )

        response = self.client.get(reverse("api:news-articles-list"))
        assert response.status_code == status.HTTP_200_OK

        expected_data = [
            {
                "id": news_article_1.id,
                "date": str(news_article_1.published_date),
                "title": news_article_1.title,
                "url": news_article_1.url,
                "source_name": source.source_display_name,
                "author": news_article_1.author,
            },
            {
                "id": news_article_2.id,
                "date": str(news_article_2.published_date),
                "title": news_article_2.title,
                "url": news_article_2.url,
                "source_name": source.source_display_name,
                "author": news_article_2.author,
            },
        ]

        assert response.data == expected_data

    def test_list_success_in_admin_mode(self):
        create_app_config = APP_CONFIG[2]

        AppValueConfigFactory(
            name=create_app_config["name"],
            value=create_app_config["value"],
            description=create_app_config["description"],
        )

        source = NewsArticleSourceFactory(source_display_name="dummy")
        officer = OfficerFactory()
        news_article_1 = NewsArticleFactory(source=source)
        news_article_2 = NewsArticleFactory(
            source=source,
            published_date=news_article_1.published_date - datetime.timedelta(days=1),
        )
        news_article_3 = NewsArticleFactory(
            source=source,
            is_hidden=True,
        )
        news_article_4 = NewsArticleFactory(
            source=source,
            published_date=news_article_1.published_date - datetime.timedelta(days=2),
        )
        news_article_5 = NewsArticleFactory(
            source=source,
            published_date=news_article_1.published_date - datetime.timedelta(days=5),
        )
        NewsArticleFactory()

        matched_sentence_1 = MatchedSentenceFactory(article=news_article_1)
        matched_sentence_2 = MatchedSentenceFactory(article=news_article_2)
        matched_sentence_3 = MatchedSentenceFactory(article=news_article_3)
        matched_sentence_4 = MatchedSentenceFactory(article=news_article_4)
        matched_sentence_5 = MatchedSentenceFactory(article=news_article_5)
        matched_sentence_1.officers.add(officer)
        matched_sentence_1.save()
        matched_sentence_2.officers.add(officer)
        matched_sentence_2.save()
        matched_sentence_3.officers.add(officer)
        matched_sentence_3.save()
        matched_sentence_4.officers.add(officer)
        matched_sentence_4.save()
        matched_sentence_5.officers.add(officer)
        matched_sentence_5.save()

        NewsArticleClassificationFactory(
            article_id=news_article_2.id,
            news_article=news_article_2,
            score=0.8,
            relevant="relevant",
        )
        NewsArticleClassificationFactory(
            article_id=news_article_4.id,
            news_article=news_article_4,
            score=0.4,
            relevant="relevant",
        )
        NewsArticleClassificationFactory(
            article_id=news_article_5.id,
            news_article=news_article_5,
            score=0.3,
            relevant="not_relevant",
        )

        response = self.admin_client.get(reverse("api:news-articles-list"))
        assert response.status_code == status.HTTP_200_OK

        expected_data = [
            {
                "id": news_article_1.id,
                "date": str(news_article_1.published_date),
                "title": news_article_1.title,
                "url": news_article_1.url,
                "source_name": source.source_display_name,
                "author": news_article_1.author,
            },
            {
                "id": news_article_2.id,
                "date": str(news_article_2.published_date),
                "title": news_article_2.title,
                "url": news_article_2.url,
                "source_name": source.source_display_name,
                "author": news_article_2.author,
            },
            {
                "id": news_article_4.id,
                "date": str(news_article_4.published_date),
                "title": news_article_4.title,
                "url": news_article_4.url,
                "source_name": source.source_display_name,
                "author": news_article_4.author,
            },
            {
                "id": news_article_5.id,
                "date": str(news_article_5.published_date),
                "title": news_article_5.title,
                "url": news_article_5.url,
                "source_name": source.source_display_name,
                "author": news_article_5.author,
            },
        ]

        assert response.data == expected_data

    @patch("news_articles.views.flush_news_article_related_caches")
    def test_hide_success(self, mock_flush_news_article_related_caches):
        officer = OfficerFactory()
        source = NewsArticleSourceFactory(source_display_name="dummy")
        news_article_1 = NewsArticleFactory(id=1, source=source, is_hidden=False)
        news_article_2 = NewsArticleFactory(id=2, source=source, is_hidden=False)
        news_article_3 = NewsArticleFactory(id=3, source=source, is_hidden=False)

        matched_sentence_1 = MatchedSentenceFactory(article=news_article_1)
        matched_sentence_2 = MatchedSentenceFactory(article=news_article_2)
        matched_sentence_3 = MatchedSentenceFactory(article=news_article_3)
        matched_sentence_1.officers.add(officer)
        matched_sentence_2.officers.add(officer)
        matched_sentence_3.officers.add(officer)

        rebuild_search_index()

        response = self.admin_client.post(
            reverse("api:news-articles-hide", kwargs={"pk": 1})
        )

        es_doc_1 = NewsArticleESDoc.get(id=1)
        es_doc_2 = NewsArticleESDoc.get(id=2)
        es_doc_3 = NewsArticleESDoc.get(id=3)

        mock_flush_news_article_related_caches.assert_called()

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"detail": "the news articles is hidden"}
        assert es_doc_1.is_hidden
        assert not es_doc_2.is_hidden
        assert not es_doc_3.is_hidden

    def test_hide_unauthorized(self):
        response = self.client.post(reverse("api:news-articles-hide", kwargs={"pk": 1}))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_hide_with_non_admin(self):
        response = self.auth_client.post(
            reverse("api:news-articles-hide", kwargs={"pk": 1})
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_hide_not_found(self):
        response = self.admin_client.post(
            reverse("api:news-articles-hide", kwargs={"pk": 1})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
