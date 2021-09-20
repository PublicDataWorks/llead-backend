from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app_config.factories import AppConfigFactory, AppTextContentFactory, FrontPageOrderFactory


class AppConfigTestCase(APITestCase):
    def test_should_return_correct_app_config(self):
        AppConfigFactory(name='CONFIG_1', value='VALUE 1')
        AppConfigFactory(name='CONFIG_2', value='VALUE 2')
        AppConfigFactory(name='CONFIG_3', value='VALUE 3')
        AppTextContentFactory(name='TEXT_CONTENT_1', value='TEXT 1')
        AppTextContentFactory(name='TEXT_CONTENT_2', value='TEXT 2')

        url = reverse('api:app-config-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == ({
            'CONFIG_1': 'VALUE 1',
            'CONFIG_2': 'VALUE 2',
            'CONFIG_3': 'VALUE 3',
            'CMS': {
                'TEXT_CONTENT_1': 'TEXT 1',
                'TEXT_CONTENT_2': 'TEXT 2',
            }
        })


class FrontPageOrderTestCase(APITestCase):
    def test_should_return_correct_front_page_order(self):
        FrontPageOrderFactory(section='TEXT_CONTENT_1', order=1)
        FrontPageOrderFactory(section='TEXT_CONTENT_2', order=2)

        url = reverse('api:front-page-orders-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == ([
            {
                'section': 'TEXT_CONTENT_1',
                'order': 1,
            },
            {
                'section': 'TEXT_CONTENT_2',
                'order': 2,
            }
        ])
