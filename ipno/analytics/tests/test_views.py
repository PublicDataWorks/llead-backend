import datetime
import pytz

from django.urls import reverse

from rest_framework import status
from freezegun import freeze_time

from test_utils.auth_api_test_case import AuthAPITestCase
from documents.factories import DocumentFactory
from departments.factories import DepartmentFactory
from officers.factories import OfficerFactory
from analytics.views import RECENT_DAYS


class AnalyticsViewSetTestCase(AuthAPITestCase):
    def test_summary(self):
        current_date = datetime.datetime.now(pytz.utc)

        with freeze_time(current_date - datetime.timedelta(days=32)):
            DocumentFactory.create_batch(4)
        with freeze_time(current_date - datetime.timedelta(days=15)):
            DocumentFactory.create_batch(3)
        with freeze_time(current_date - datetime.timedelta(days=35)):
            OfficerFactory.create_batch(3)
        with freeze_time(current_date - datetime.timedelta(days=12)):
            OfficerFactory.create_batch(2)
        with freeze_time(current_date - datetime.timedelta(days=40)):
            DepartmentFactory.create_batch(2)
        with freeze_time(current_date - datetime.timedelta(days=2)):
            DepartmentFactory.create_batch(1)

        url = reverse('api:analytics-summary')
        response = self.auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == ({
            'documents_count': 7,
            'officers_count': 5,
            'departments_count': 3,
            'recent_documents_count': 3,
            'recent_officers_count': 2,
            'recent_departments_count': 1,
            'recent_days': RECENT_DAYS,
        })
