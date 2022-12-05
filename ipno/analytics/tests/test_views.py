from django.urls import reverse

from rest_framework import status

from complaints.factories import ComplaintFactory
from departments.factories import DepartmentFactory
from documents.factories import DocumentFactory
from news_articles.factories import NewsArticleFactory
from officers.factories import OfficerFactory
from people.factories import PersonFactory
from test_utils.auth_api_test_case import AuthAPITestCase
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

        url = reverse("api:analytics-summary")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == (
            {
                "documents_count": 8,
                "officers_count": 5,
                "departments_count": 6,
                "news_articles_count": 10,
            }
        )

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

        url = reverse("api:analytics-summary")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == (
            {
                "documents_count": 8,
                "officers_count": 7,
                "departments_count": 6,
                "news_articles_count": 10,
            }
        )
