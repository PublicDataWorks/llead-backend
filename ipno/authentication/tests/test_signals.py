from collections import namedtuple

from django.conf import settings
from django.template.loader import render_to_string
from django.test.testcases import TestCase

from django_rest_passwordreset.signals import reset_password_token_created
from mock import patch

from app_config.factories import AppTextContentFactory
from authentication.factories import UserFactory
from authentication.signals import password_reset_token_created


class AuthenticationTestCase(TestCase):
    @patch("authentication.signals.send_mail")
    def test_password_reset_token_created(self, mock_send_mail):
        reset_password_template = (
            "Reset password link: {HOST}/?token={reset_password_token}"
        )
        AppTextContentFactory(
            name="FORGOT_PASSWORD_EMAIL", value=reset_password_template
        )

        password_token = namedtuple("password_token", ["key", "user"])
        token = "t0ken"
        email = "user@email.com"
        user = UserFactory(email=email)
        reset_password_token = password_token(key=token, user=user)

        reset_password_token_created.connect(password_reset_token_created)
        reset_password_token_created.send(
            sender="test", instance=None, reset_password_token=reset_password_token
        )

        message = reset_password_template.replace(
            "{reset_password_token}", token
        ).replace("{HOST}", settings.HOST)
        mock_send_mail.assert_called_with(
            subject="Password Reset",
            from_email=settings.FROM_EMAIL,
            recipient_list=[user.email],
            html_message=render_to_string(
                "email/dynamic_email.html", {"message": message}
            ),
            message=render_to_string("email/dynamic_email.html", {"message": message}),
        )
