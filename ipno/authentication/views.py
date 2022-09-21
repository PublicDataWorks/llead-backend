from datetime import timedelta

from django.contrib.auth.password_validation import validate_password, get_password_validators
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.vary import vary_on_headers

from rest_framework import exceptions
from rest_framework.serializers import Serializer, CharField
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django_rest_passwordreset.models import ResetPasswordToken
from django_rest_passwordreset.signals import pre_password_reset, post_password_reset
from django_rest_passwordreset.views import get_password_reset_token_expiry_time

from authentication.serializers import UserSerializer
from utils.cache_utils import custom_cache


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

    @method_decorator(vary_on_headers("Authorization", ))
    @custom_cache
    def get(self, request):
        user = request.user
        return Response(UserSerializer(user).data)


class CustomPasswordTokenVerificationView(APIView):
    class CustomTokenSerializer(Serializer):
        token = CharField()
        password = CharField()

    throttle_classes = ()
    permission_classes = ()
    serializer_class = CustomTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data['password']
        token = serializer.validated_data['token']

        reset_password_token = ResetPasswordToken.objects.filter(key=token).first()

        if reset_password_token is None:
            return Response({'message': 'Token is invalid or has been used.'}, status=HTTP_404_NOT_FOUND)

        password_reset_token_validation_time = get_password_reset_token_expiry_time()
        expiry_date = reset_password_token.created_at + timedelta(hours=password_reset_token_validation_time)

        if timezone.now() > expiry_date:
            reset_password_token.delete()
            return Response({'message': 'Token is expired.'}, status=HTTP_404_NOT_FOUND)

        reset_password_token.user.eligible_for_reset()

        pre_password_reset.send(sender=self.__class__, user=reset_password_token.user)
        try:
            validate_password(
                password,
                user=reset_password_token.user,
                password_validators=get_password_validators(settings.AUTH_PASSWORD_VALIDATORS)
            )
        except ValidationError as e:
            raise exceptions.ValidationError({
                'message': ' '.join(e.messages)
            })

        reset_password_token.user.set_password(password)
        reset_password_token.user.save()
        post_password_reset.send(sender=self.__class__, user=reset_password_token.user)

        ResetPasswordToken.objects.filter(user=reset_password_token.user).delete()

        return Response({'message': 'Your password has changed.'})
