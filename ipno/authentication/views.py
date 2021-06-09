from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.serializers import UserSerializer


class TokenRevokeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        refresh_data = request.data.get('refresh')
        try:
            refresh_token = RefreshToken(refresh_data)
        except TokenError as e:
            return Response({'detail': str(e), 'code': 'token_not_valid'}, status=HTTP_401_UNAUTHORIZED)

        user = request.user
        if user.id != refresh_token.get('user_id'):
            return Response({"detail": "Token is invalid", "code": "token_not_valid"},
                            status=HTTP_400_BAD_REQUEST)

        refresh_token.blacklist()
        return Response({'detail': 'Logout successfully'})


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(UserSerializer(user).data)
