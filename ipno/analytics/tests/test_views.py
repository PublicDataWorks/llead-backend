from django.urls import reverse

from rest_framework import status

from complaints.factories import ComplaintFactory
from news_articles.factories import NewsArticleFactory
from officers.factories import OfficerFactory
from people.factories import PersonFactory
from test_utils.auth_api_test_case import AuthAPITestCase
from documents.factories import DocumentFactory
from departments.factories import DepartmentFactory
from use_of_forces.factories import UseOfForceFactory


class AnalyticsViewSetTestCase(AuthAPITestCase):
    def test_summary(self):
        DocumentFactory.create_batch(7)
        NewsArticleFactory.create_batch(10)
        PersonFactory.create_batch(5)

        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()
        department_3 = DepartmentFactory()
        DepartmentFactory()

        document = DocumentFactory()
        document.departments.add(department_1)

        UseOfForceFactory(department=department_2)

        complaint = ComplaintFactory()
        complaint.departments.add(department_3)
        department_4 = DepartmentFactory()
        DepartmentFactory()

        UseOfForceFactory(department=department_4)

        url = reverse('api:analytics-summary')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == ({
            'documents_count': 8,
            'officers_count': 5,
            'departments_count': 4,
            'news_articles_count': 10,
        })

    def test_summary_with_related_officer(self):
        DocumentFactory.create_batch(7)
        NewsArticleFactory.create_batch(10)

        PersonFactory.create_batch(3)
        officer = OfficerFactory()
        person = PersonFactory(canonical_officer=officer)
        officer.person = person
        officer.save()
        OfficerFactory(person=person)

        PersonFactory.create_batch(2)
        officer = OfficerFactory()
        person = PersonFactory(canonical_officer=officer)
        officer.person = person
        officer.save()
        OfficerFactory(person=person)

        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()
        department_3 = DepartmentFactory()
        DepartmentFactory()

        document = DocumentFactory()
        document.departments.add(department_1)

        UseOfForceFactory(department=department_2)

        complaint = ComplaintFactory()
        complaint.departments.add(department_3)

        department_4 = DepartmentFactory()
        DepartmentFactory()

        UseOfForceFactory(department=department_4)

        url = reverse('api:analytics-summary')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == ({
            'documents_count': 8,
            'officers_count': 7,
            'departments_count': 4,
            'news_articles_count': 10,
        })

    def test_department_count_with_only_document(self):
        department_1 = DepartmentFactory()
        DepartmentFactory()

        document_1 = DocumentFactory()
        document_1.departments.add(department_1)

        department_2 = DepartmentFactory()
        DepartmentFactory()

        document_2 = DocumentFactory()
        document_2.departments.add(department_2)

        url = reverse('api:analytics-summary')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == ({
            'documents_count': 2,
            'officers_count': 0,
            'departments_count': 2,
            'news_articles_count': 0,
        })

    def test_department_count_with_only_use_of_force(self):
        department_1 = DepartmentFactory()
        DepartmentFactory()

        UseOfForceFactory(department=department_1)

        department_2 = DepartmentFactory()
        DepartmentFactory()

        UseOfForceFactory(department=department_2)

        url = reverse('api:analytics-summary')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == ({
            'documents_count': 0,
            'officers_count': 0,
            'departments_count': 2,
            'news_articles_count': 0,
        })

    def test_department_count_with_only_complaint(self):
        department_1 = DepartmentFactory()
        DepartmentFactory()

        complaint_1 = ComplaintFactory()
        complaint_1.departments.add(department_1)

        department_2 = DepartmentFactory()
        DepartmentFactory()

        complaint_2 = ComplaintFactory()
        complaint_2.departments.add(department_2)

        url = reverse('api:analytics-summary')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == ({
            'documents_count': 0,
            'officers_count': 0,
            'departments_count': 2,
            'news_articles_count': 0,
        })
