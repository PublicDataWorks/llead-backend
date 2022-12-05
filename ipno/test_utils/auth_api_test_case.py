from rest_framework.test import APIClient, APITestCase

from rest_framework_simplejwt.tokens import RefreshToken

from authentication.factories import UserFactory


class AuthAPITestCase(APITestCase):
    def setUp(self):
        user = UserFactory(email="username@email.com")
        admin = UserFactory(
            email="admin@email.com",
            is_admin=True,
        )

        user_refresh_token = RefreshToken.for_user(user)
        admin_refresh_token = RefreshToken.for_user(admin)

        self.user = user
        self.admin = admin

        self.auth_client = APIClient()
        self.auth_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(user_refresh_token.access_token)}"
        )

        self.admin_client = APIClient()
        self.admin_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(admin_refresh_token.access_token)}"
        )
