from django.urls import reverse
from rest_framework import status

from q_and_a.factories import SectionFactory, QuestionFactory
from test_utils.auth_api_test_case import AuthAPITestCase


class QuestionAndAnswerTestCase(AuthAPITestCase):
    def test_retrieve_unauthorized(self):
        url = reverse('api:q-and-a-list')
        response = self.client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_correctly(self):
        section = SectionFactory()
        question = QuestionFactory(section=section)

        url = reverse('api:q-and-a-list')
        response = self.auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == [
            {
                'section': section.name,
                'q_and_a': [
                    {
                        'question': question.question,
                        'answer': question.answer,
                    }
                ]
            }
        ]
