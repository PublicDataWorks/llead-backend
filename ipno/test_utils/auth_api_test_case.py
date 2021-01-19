from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.factories import UserFactory


class AuthAPITestCase(APITestCase):
    def setUp(self):
        user = UserFactory(email='username@email.com')
        refresh_token = RefreshToken.for_user(user)

        self.user = user
        self.auth_client = APIClient()
        self.auth_client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh_token.access_token)}')
