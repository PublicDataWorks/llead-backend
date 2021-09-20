import datetime

from django.urls import reverse
from rest_framework import status

from authentication.models import User
from news_articles.factories import NewsArticleFactory, NewsArticleSourceFactory
from test_utils.auth_api_test_case import AuthAPITestCase
from officers.factories import OfficerFactory, EventFactory
from departments.factories import DepartmentFactory
from documents.factories import DocumentFactory
from historical_data.constants import (
    RECENT_DEPARTMENT_TYPE,
    RECENT_DOCUMENT_TYPE,
    RECENT_NEWS_ARTICLE_TYPE,
    RECENT_OFFICER_TYPE,
)


class HistoricalDataViewSetTestCase(AuthAPITestCase):
    def test_recent_items(self):
        department_1 = DepartmentFactory(name='Baton Rouge PD')
        department_2 = DepartmentFactory(name='New Orleans PD')

        officer = OfficerFactory(first_name='David', last_name='Jonesworth')
        EventFactory(
            officer=officer,
            department=department_2,
            badge_no='12435',
        )

        source = NewsArticleSourceFactory()
        news_article = NewsArticleFactory(
            published_date=datetime.datetime(2021, 9, 7).date(),
            source=source
        )

        document = DocumentFactory()
        document.departments.add(department_1)

        DepartmentFactory()
        OfficerFactory()
        DocumentFactory()

        self.user.recent_items = [
            {
                'type': RECENT_DOCUMENT_TYPE,
                'id': document.id
            },
            {
                'type': RECENT_DEPARTMENT_TYPE,
                'id': department_1.slug
            },
            {
                'type': RECENT_OFFICER_TYPE,
                'id': officer.id
            },
            {
                'type': RECENT_DEPARTMENT_TYPE,
                'id': department_2.slug
            },
            {
                'type': RECENT_DEPARTMENT_TYPE,
                'id': 'falsy-slug',
            },
            {
                'type': RECENT_OFFICER_TYPE,
                'id': '-1',
            },
            {
                'type': RECENT_NEWS_ARTICLE_TYPE,
                'id': news_article.id,
            }
        ]
        self.user.save()

        response = self.auth_client.get(
            reverse('api:historical-data-recent-items')
        )

        expected_data = [
            {
                'id': document.id,
                'document_type': document.document_type,
                'title': document.title,
                'url': document.url,
                'preview_image_url': document.preview_image_url,
                'incident_date': str(document.incident_date),
                'pages_count': document.pages_count,
                'departments': [
                    {
                        'id': department_1.slug,
                        'name': department_1.name,
                    }
                ],
                'type': RECENT_DOCUMENT_TYPE
            },
            {
                'id': department_1.slug,
                'name': department_1.name,
                'city': department_1.city,
                'parish': department_1.parish,
                'location_map_url': department_1.location_map_url,
                'type': RECENT_DEPARTMENT_TYPE
            },
            {
                'id': officer.id,
                'name': 'David Jonesworth',
                'badges': ['12435'],
                'department': {
                    'id': department_2.slug,
                    'name': department_2.name,
                },
                'type': RECENT_OFFICER_TYPE
            },
            {
                'id': department_2.slug,
                'name': department_2.name,
                'city': department_2.city,
                'parish': department_2.parish,
                'location_map_url': department_2.location_map_url,
                'type': RECENT_DEPARTMENT_TYPE
            },
            {
                'id': news_article.id,
                'source_name': source.custom_matching_name,
                'title': news_article.title,
                'url': news_article.url,
                'date': '2021-09-07',
                'type': 'NEWS_ARTICLE',
            }
        ]

        result = response.data

        assert response.status_code == status.HTTP_200_OK
        assert result == expected_data

    def test_no_recent_items(self):
        response = self.auth_client.get(
            reverse('api:historical-data-recent-items')
        )
        result = response.data

        assert response.status_code == status.HTTP_200_OK
        assert result == []

    def test_update_new_recent_items(self):
        department_1 = DepartmentFactory(name='Baton Rouge PD')
        department_2 = DepartmentFactory(name='New Orleans PD')

        officer = OfficerFactory(first_name='David', last_name='Jonesworth')
        EventFactory(
            officer=officer,
            department=department_2,
            badge_no='12435',
        )

        document = DocumentFactory()
        document.departments.add(department_1)

        DepartmentFactory()
        OfficerFactory()
        DocumentFactory()

        old_recent_item = [
            {
                'type': RECENT_DOCUMENT_TYPE,
                'id': document.id
            },
            {
                'type': RECENT_DEPARTMENT_TYPE,
                'id': department_1.slug
            },
            {
                'type': RECENT_OFFICER_TYPE,
                'id': officer.id
            }
        ]

        self.user.recent_items = old_recent_item
        self.user.save()

        data = {
            'type': RECENT_DEPARTMENT_TYPE,
            'id': department_2.slug
        }

        response = self.auth_client.post(
            reverse('api:historical-data-recent-items'),
            data,
            format='json'
        )

        expected_data = {'detail': 'updated user recent items'}

        result = response.data

        user = User.objects.first()

        assert response.status_code == status.HTTP_200_OK
        assert result == expected_data
        assert user.recent_items == [data, *old_recent_item]

    def test_update_existed_recent_items(self):
        department_1 = DepartmentFactory(name='Baton Rouge PD')
        department_2 = DepartmentFactory(name='New Orleans PD')

        officer = OfficerFactory(first_name='David', last_name='Jonesworth')
        EventFactory(
            officer=officer,
            department=department_2,
            badge_no='12435',
        )

        document = DocumentFactory()
        document.departments.add(department_1)

        DepartmentFactory()
        OfficerFactory()
        DocumentFactory()

        old_recent_item = [
            {
                'type': RECENT_DOCUMENT_TYPE,
                'id': document.id
            },
            {
                'type': RECENT_DEPARTMENT_TYPE,
                'id': department_1.slug
            },
            {
                'type': RECENT_OFFICER_TYPE,
                'id': officer.id
            }
        ]

        self.user.recent_items = old_recent_item
        self.user.save()

        data = {
            'type': RECENT_DEPARTMENT_TYPE,
            'id': department_1.slug
        }

        response = self.auth_client.post(
            reverse('api:historical-data-recent-items'),
            data,
            format='json'
        )

        expected_data = {'detail': 'updated user recent items'}

        result = response.data

        user = User.objects.first()

        assert response.status_code == status.HTTP_200_OK
        assert result == expected_data
        assert user.recent_items == [
            {
                'type': RECENT_DEPARTMENT_TYPE,
                'id': department_1.slug
            },
            {
                'type': RECENT_DOCUMENT_TYPE,
                'id': document.id
            },
            {
                'type': RECENT_OFFICER_TYPE,
                'id': officer.id
            }
        ]

    def test_recent_queries(self):
        self.user.recent_queries = ['query 2', 'query 1']
        self.user.save()

        response = self.auth_client.get(
            reverse('api:historical-data-recent-queries')
        )
        result = response.data

        assert response.status_code == status.HTTP_200_OK
        assert result == ['query 2', 'query 1']

    def test_no_recent_queries(self):
        response = self.auth_client.get(
            reverse('api:historical-data-recent-queries')
        )
        result = response.data

        assert response.status_code == status.HTTP_200_OK
        assert not result

    def test_update_new_recent_queries(self):

        self.user.recent_queries = ['query 2', 'query 1']
        self.user.save()

        data = {'q': 'query 3'}

        response = self.auth_client.post(
            reverse('api:historical-data-recent-queries'),
            data,
            format='json'
        )

        expected_data = {'detail': 'updated user recent queries'}

        result = response.data

        user = User.objects.first()

        assert response.status_code == status.HTTP_200_OK
        assert result == expected_data
        assert user.recent_queries == [data.get('q'), 'query 2', 'query 1']

    def test_update_existed_recent_queries(self):
        self.user.recent_queries = ['query 2', 'query 1']
        self.user.save()

        data = {'q': 'query 1'}

        response = self.auth_client.post(
            reverse('api:historical-data-recent-queries'),
            data,
            format='json'
        )

        expected_data = {'detail': 'updated user recent queries'}

        result = response.data

        user = User.objects.first()

        assert response.status_code == status.HTTP_200_OK
        assert result == expected_data
        assert user.recent_queries == ['query 1', 'query 2']
