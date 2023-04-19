from django.urls import reverse

from rest_framework import status

from findings.factories import FindingFactory
from test_utils.auth_api_test_case import AuthAPITestCase


class FindingsTestCase(AuthAPITestCase):
    def test_list_correctly(self):
        findings = FindingFactory()

        url = reverse("findings")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "background_image_url": None,
            "title": findings.title,
            "description": findings.description,
            "card_image_url": None,
            "card_title": findings.card_title,
            "card_author": findings.card_author,
            "card_department": findings.card_department,
        }
