from mock import patch

from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status


class QuestionAndAnswerTestCase(APITestCase):
    @patch('feedbacks.views.send_mail')
    def test_submit_message_successfully(self, mock_send_mail):
        url = reverse('api:feedbacks-list')

        email = 'email@gmail.com'
        message = 'Test message'

        context = {
            "message": f"Message from {email}: {message}"
        }

        response = self.client.post(
            url,
            {
                'email': email,
                'message': message
            },
            format='json',
        )

        mock_send_mail.assert_called_with(
            subject="IPNO message from contact page",
            from_email=settings.FEEDBACK_FROM_EMAIL,
            recipient_list=[settings.FEEDBACK_TO_EMAIL],
            html_message=render_to_string("email/dynamic_email.html", context),
            message=render_to_string("email/dynamic_email.html", context)
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'detail': 'Your message has been submitted'
        }
