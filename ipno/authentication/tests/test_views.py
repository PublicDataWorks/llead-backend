from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.factories import UserFactory


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
