from django.test import TestCase

from authentication.models import User
from authentication.serializers import UserSerializer


class UserSerializerTestCase(TestCase):
    def test_user_data(self):
        email = 'user@mail.com'
        user = User.objects.create_user(email, 'p@ssw0rd')
        user_data = UserSerializer(user).data

        assert user_data == {
            'email': email,
            'is_admin': False,
        }
