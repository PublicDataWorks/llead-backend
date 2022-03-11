import datetime
import pytz

from django.urls import reverse

from rest_framework import status
from freezegun import freeze_time

from app_config.models import AppConfig
from complaints.factories import ComplaintFactory
from officers.factories import OfficerFactory
from people.factories import PersonFactory
from test_utils.auth_api_test_case import AuthAPITestCase
from documents.factories import DocumentFactory
from departments.factories import DepartmentFactory
from analytics.views import DEFAULT_RECENT_DAYS
from use_of_forces.factories import UseOfForceFactory


class AnalyticsViewSetTestCase(AuthAPITestCase):
    def test_summary(self):
        recent_days = 34
        AppConfig.objects.create(name='ANALYTIC_RECENT_DAYS', value=recent_days)

        current_date = datetime.datetime.now(pytz.utc)

        with freeze_time(current_date - datetime.timedelta(days=32)):
            DocumentFactory.create_batch(4)
        with freeze_time(current_date - datetime.timedelta(days=15)):
            DocumentFactory.create_batch(3)
        with freeze_time(current_date - datetime.timedelta(days=35)):
            PersonFactory.create_batch(3)
        with freeze_time(current_date - datetime.timedelta(days=12)):
            PersonFactory.create_batch(2)
        with freeze_time(current_date - datetime.timedelta(days=40)):
            department_1 = DepartmentFactory()
            department_2 = DepartmentFactory()
            department_3 = DepartmentFactory()
            DepartmentFactory()

            document = DocumentFactory()
            document.departments.add(department_1)

            UseOfForceFactory(department=department_2)

            complaint = ComplaintFactory()
            complaint.departments.add(department_3)
        with freeze_time(current_date - datetime.timedelta(days=2)):
            department_4 = DepartmentFactory()
            DepartmentFactory()

            UseOfForceFactory(department=department_4)

        url = reverse('api:analytics-summary')
        response = self.auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == ({
            'documents_count': 8,
            'officers_count': 5,
            'departments_count': 4,
            'recent_documents_count': 7,
            'recent_officers_count': 2,
            'recent_departments_count': 1,
            'recent_days': recent_days,
        })

    def test_summary_default_recent_days(self):
        current_date = datetime.datetime.now(pytz.utc)

        with freeze_time(current_date - datetime.timedelta(days=32)):
            DocumentFactory.create_batch(4)
        with freeze_time(current_date - datetime.timedelta(days=15)):
            DocumentFactory.create_batch(3)
        with freeze_time(current_date - datetime.timedelta(days=35)):
            PersonFactory.create_batch(3)
        with freeze_time(current_date - datetime.timedelta(days=12)):
            PersonFactory.create_batch(2)
        with freeze_time(current_date - datetime.timedelta(days=40)):
            department_1 = DepartmentFactory()
            department_2 = DepartmentFactory()
            department_3 = DepartmentFactory()
            DepartmentFactory()

            document = DocumentFactory()
            document.departments.add(department_1)

            UseOfForceFactory(department=department_2)

            complaint = ComplaintFactory()
            complaint.departments.add(department_3)
        with freeze_time(current_date - datetime.timedelta(days=2)):
            department_4 = DepartmentFactory()
            DepartmentFactory()

            UseOfForceFactory(department=department_4)

        url = reverse('api:analytics-summary')
        response = self.auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == ({
            'documents_count': 8,
            'officers_count': 5,
            'departments_count': 4,
            'recent_documents_count': 3,
            'recent_officers_count': 2,
            'recent_departments_count': 1,
            'recent_days': DEFAULT_RECENT_DAYS,
        })

    def test_summary_with_related_officer(self):
        recent_days = 34
        AppConfig.objects.create(name='ANALYTIC_RECENT_DAYS', value=recent_days)

        current_date = datetime.datetime.now(pytz.utc)

        with freeze_time(current_date - datetime.timedelta(days=32)):
            DocumentFactory.create_batch(4)
        with freeze_time(current_date - datetime.timedelta(days=15)):
            DocumentFactory.create_batch(3)
        with freeze_time(current_date - datetime.timedelta(days=35)):
            PersonFactory.create_batch(3)
            officer = OfficerFactory()
            person = PersonFactory(canonical_officer=officer)
            officer.person = person
            officer.save()
            OfficerFactory(person=person)
        with freeze_time(current_date - datetime.timedelta(days=12)):
            PersonFactory.create_batch(2)
            officer = OfficerFactory()
            person = PersonFactory(canonical_officer=officer)
            officer.person = person
            officer.save()
            OfficerFactory(person=person)
        with freeze_time(current_date - datetime.timedelta(days=40)):
            department_1 = DepartmentFactory()
            department_2 = DepartmentFactory()
            department_3 = DepartmentFactory()
            DepartmentFactory()

            document = DocumentFactory()
            document.departments.add(department_1)

            UseOfForceFactory(department=department_2)

            complaint = ComplaintFactory()
            complaint.departments.add(department_3)
        with freeze_time(current_date - datetime.timedelta(days=2)):
            department_4 = DepartmentFactory()
            DepartmentFactory()

            UseOfForceFactory(department=department_4)

        url = reverse('api:analytics-summary')
        response = self.auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == ({
            'documents_count': 8,
            'officers_count': 7,
            'departments_count': 4,
            'recent_documents_count': 7,
            'recent_officers_count': 3,
            'recent_departments_count': 1,
            'recent_days': recent_days,
        })

    def test_department_count_with_only_document(self):
        recent_days = 34
        AppConfig.objects.create(name='ANALYTIC_RECENT_DAYS', value=recent_days)

        current_date = datetime.datetime.now(pytz.utc)

        with freeze_time(current_date - datetime.timedelta(days=40)):
            department_1 = DepartmentFactory()
            DepartmentFactory()

            document_1 = DocumentFactory()
            document_1.departments.add(department_1)

        with freeze_time(current_date - datetime.timedelta(days=2)):
            department_2 = DepartmentFactory()
            DepartmentFactory()

            document_2 = DocumentFactory()
            document_2.departments.add(department_2)

        url = reverse('api:analytics-summary')
        response = self.auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == ({
            'documents_count': 2,
            'officers_count': 0,
            'departments_count': 2,
            'recent_documents_count': 1,
            'recent_officers_count': 0,
            'recent_departments_count': 1,
            'recent_days': recent_days,
        })

    def test_department_count_with_only_use_of_force(self):
        recent_days = 34
        AppConfig.objects.create(name='ANALYTIC_RECENT_DAYS', value=recent_days)

        current_date = datetime.datetime.now(pytz.utc)

        with freeze_time(current_date - datetime.timedelta(days=40)):
            department_1 = DepartmentFactory()
            DepartmentFactory()

            UseOfForceFactory(department=department_1)

        with freeze_time(current_date - datetime.timedelta(days=2)):
            department_2 = DepartmentFactory()
            DepartmentFactory()

            UseOfForceFactory(department=department_2)

        url = reverse('api:analytics-summary')
        response = self.auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == ({
            'documents_count': 0,
            'officers_count': 0,
            'departments_count': 2,
            'recent_documents_count': 0,
            'recent_officers_count': 0,
            'recent_departments_count': 1,
            'recent_days': recent_days,
        })

    def test_department_count_with_only_complaint(self):
        recent_days = 34
        AppConfig.objects.create(name='ANALYTIC_RECENT_DAYS', value=recent_days)

        current_date = datetime.datetime.now(pytz.utc)

        with freeze_time(current_date - datetime.timedelta(days=40)):
            department_1 = DepartmentFactory()
            DepartmentFactory()

            complaint_1 = ComplaintFactory()
            complaint_1.departments.add(department_1)

        with freeze_time(current_date - datetime.timedelta(days=2)):
            department_2 = DepartmentFactory()
            DepartmentFactory()

            complaint_2 = ComplaintFactory()
            complaint_2.departments.add(department_2)

        url = reverse('api:analytics-summary')
        response = self.auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == ({
            'documents_count': 0,
            'officers_count': 0,
            'departments_count': 2,
            'recent_documents_count': 0,
            'recent_officers_count': 0,
            'recent_departments_count': 1,
            'recent_days': recent_days,
        })
