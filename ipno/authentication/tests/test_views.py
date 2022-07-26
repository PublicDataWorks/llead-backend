from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from django_rest_passwordreset.models import ResetPasswordToken

from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from django_rest_passwordreset.signals import reset_password_token_created

from app_config.factories import AppTextContentFactory
from authentication.factories import UserFactory
from test_utils.auth_api_test_case import AuthAPITestCase


class TokenObtainPairViewTestCase(APITestCase):
    def test_token_success(self):
        user = UserFactory(email='mail@mail.com', raw_password='abc@123')
        response = self.client.post(reverse('token'), {
            'email': 'mail@mail.com',
            'password': 'abc@123'
        })

        access_token = response.data['access']

        assert response.status_code == status.HTTP_200_OK
        assert access_token
        assert response.data['refresh']

        jwt_auth = JWTTokenUserAuthentication()
        validated_token = jwt_auth.get_validated_token(access_token)

        assert validated_token['user_id'] == user.id

    def test_token_failed(self):
        UserFactory(email='mail@mail.com', raw_password='abc@123')
        response = self.client.post(reverse('token'), {
            'email': 'invalid@mail.com',
            'password': 'abc@123'
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TokenRefreshViewTestCase(APITestCase):
    def test_refresh_token_success(self):
        user = UserFactory()
        refresh_token = RefreshToken.for_user(user)

        response = self.client.post(reverse('refresh_token'), {
            'refresh': str(refresh_token)
        })

        access_token = response.data['access']

        assert response.status_code == status.HTTP_200_OK
        assert access_token

        jwt_auth = JWTTokenUserAuthentication()
        validated_token = jwt_auth.get_validated_token(access_token)

        assert validated_token['user_id'] == user.id


class TokenRevokeViewTestCase(AuthAPITestCase):
    def test_refresh_token_revoke_success(self):
        user = self.user
        refresh_token = RefreshToken.for_user(user)

        response = self.auth_client.post(reverse('revoke_token'), {
            'refresh': str(refresh_token)
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['detail'] == 'Logout successfully'

    def test_refresh_token_error_if_token_is_blacklisted(self):
        user = self.user
        refresh_token = RefreshToken.for_user(user)
        refresh_token.blacklist()

        response = self.auth_client.post(reverse('revoke_token'), {
            'refresh': str(refresh_token)
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['detail'] == 'Token is blacklisted'

    def test_refresh_token_error_if_token_is_not_match_with_access_token(self):
        user = UserFactory()
        refresh_token = RefreshToken.for_user(user)

        response = self.auth_client.post(reverse('revoke_token'), {
            'refresh': str(refresh_token)
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['detail'] == 'Token is invalid'


class UserViewTestCase(AuthAPITestCase):
    def test_get_user_data_success(self):
        user = self.user

        response = self.auth_client.get(reverse('user'))

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "email": user.email,
            "is_admin": user.is_admin
        }


class ForgotPasswordViewTestCase(AuthAPITestCase):
    def test_post_forgot_password(self):
        reset_password_template = "Reset password link: {HOST}/?token={reset_password_token}"
        AppTextContentFactory(name='FORGOT_PASSWORD_EMAIL', value=reset_password_template)
        user = self.user

        response = self.auth_client.post(reverse('reset-password-request'), {'email': user.email})

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "status": "OK"
        }

    def test_post_forgot_password_not_existed_email(self):
        reset_password_template = "Reset password link: {HOST}/?token={reset_password_token}"
        AppTextContentFactory(name='FORGOT_PASSWORD_EMAIL', value=reset_password_template)
        user = self.user

        response = self.auth_client.post(reverse('reset-password-request'), {'email': user.email+'.vn'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {
            "email": [
                "We couldn't find an account associated with that email. Please try a different e-mail address."
            ]
        }

    def test_post_confirm_change_password(self):
        reset_password_template = "Reset password link: {HOST}/?token={reset_password_token}"
        AppTextContentFactory(name='FORGOT_PASSWORD_EMAIL', value=reset_password_template)
        user = self.user
        token = None

        def stub_password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
            nonlocal token
            token = reset_password_token.key

        reset_password_token_created.connect(stub_password_reset_token_created)

        self.user.set_password('Old_pass')
        self.user.save()
        self.auth_client.post(reverse('reset-password-request'), {'email': user.email})

        context = {
            'token': token,
            'password': 'New_pass'
        }
        response = self.auth_client.post(reverse('reset-password-confirm'), context)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "message": "Your password has changed."
        }

        self.user.refresh_from_db()
        assert self.user.check_password('New_pass')

    def test_post_confirm_change_password_wrong_token(self):
        context = {
            'token': 'wrong_token',
            'password': 'New_pass'
        }
        response = self.auth_client.post(reverse('reset-password-confirm'), context)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == {
            "message": "Token is invalid or has been used."
        }

    def test_post_confirm_change_password_expired_token(self):
        current_time = timezone.now()
        token = None

        reset_password_template = "Reset password link: {HOST}/?token={reset_password_token}"
        AppTextContentFactory(name='FORGOT_PASSWORD_EMAIL', value=reset_password_template)
        user = self.user

        def stub_password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
            nonlocal token
            token = reset_password_token.key

        reset_password_token_created.connect(stub_password_reset_token_created)

        self.user.set_password('Old_pass')
        self.user.save()
        self.auth_client.post(reverse('reset-password-request'), {'email': user.email})

        expired_time = current_time - timedelta(days=1, hours=1)
        reset_password_token = ResetPasswordToken.objects.filter(key=token).first()
        reset_password_token.created_at = expired_time
        reset_password_token.save()

        context = {
            'token': token,
            'password': '12345678'
        }
        response = self.auth_client.post(reverse('reset-password-confirm'), context)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert str(response.data['message']) == "Token is expired."

    def test_post_confirm_change_password_validation_failed(self):
        reset_password_template = "Reset password link: {HOST}/?token={reset_password_token}"
        AppTextContentFactory(name='FORGOT_PASSWORD_EMAIL', value=reset_password_template)
        user = self.user
        token = None

        def stub_password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
            nonlocal token
            token = reset_password_token.key

        reset_password_token_created.connect(stub_password_reset_token_created)

        self.user.set_password('Old_pass')
        self.user.save()
        self.auth_client.post(reverse('reset-password-request'), {'email': user.email})

        context = {
            'token': token,
            'password': '12345678'
        }
        response = self.auth_client.post(reverse('reset-password-confirm'), context)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data['message']) == "This password is too common. This password is entirely numeric."

    def test_post_confirm_change_password_user_not_eligible(self):
        reset_password_template = "Reset password link: {HOST}/?token={reset_password_token}"
        AppTextContentFactory(name='FORGOT_PASSWORD_EMAIL', value=reset_password_template)
        user = self.user
        token = None

        def stub_password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
            nonlocal token
            token = reset_password_token.key

        reset_password_token_created.connect(stub_password_reset_token_created)

        self.user.set_password('Old_pass')
        self.user.save()
        self.auth_client.post(reverse('reset-password-request'), {'email': user.email})

        self.user.is_active = False
        self.user.save()

        context = {
            'token': token,
            'password': 'New_pass'
        }
        response = self.auth_client.post(reverse('reset-password-confirm'), context)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
