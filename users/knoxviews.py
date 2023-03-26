from django.contrib.auth import login
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models import Q, QuerySet
from django.http import HttpRequest
from django.utils import timezone
from knox.auth import TokenAuthentication
from knox.models import AuthToken
from knox.settings import knox_settings
from knox.views import LoginView as KnoxLoginView
from rest_framework import permissions, status
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.knox_serializers import (
    LoginSerializer,
    LogoutAllSerializer,
    LogoutSerializer,
)
from users.serializers import UserSerializer


class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = []
    serializer_class = LoginSerializer
    user_serializer_class = UserSerializer

    def get_user_serializer_class(self):
        return UserSerializer

    def post(self, request: HttpRequest, format=None):
        serializer = LoginSerializer(data=request.data)
        token_limit_per_user = self.get_token_limit_per_user()
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        # login(request, user)
        if token_limit_per_user is not None:
            now = timezone.now()
            token: QuerySet[AuthToken] = user.auth_token_set.filter(
                Q(expiry__gt=now) | Q(expiry__isnull=True)
            )
            if token.count() >= token_limit_per_user:
                # delete the oldest valid token for the sake of the new token
                oldest_valid_token = token.order_by("created").first()
                oldest_valid_token.delete()
        token_ttl = self.get_token_ttl()
        _, token = AuthToken.objects.create(user, token_ttl)
        user_logged_in.send(sender=user.__class__, request=request, user=user)
        res = Response(serializer.data)
        res.set_cookie(
            knox_settings.AUTH_HEADER_PREFIX,
            token,
            # samesite="None",
            # secure=True,
            max_age=1000000,
            httponly=True,
        )
        return res


class LogoutView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    def post(self, request, format=None):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if digest := serializer.validated_data.get("digest"):
            try:
                token: AuthToken = AuthToken.objects.get(
                    digest=digest, user=request.user
                )
                token.delete()
            except AuthToken.DoesNotExist:
                return Response("Token not found", status.HTTP_404_NOT_FOUND)
        else:
            request._auth.delete()
        user_logged_out.send(
            sender=request.user.__class__, request=request, user=request.user
        )
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class LogoutAllView(GenericAPIView):
    """
    Log the user out of all sessions
    I.E. deletes all auth tokens for the user
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutAllSerializer

    def post(self, request, format=None):
        request.user.auth_token_set.all().delete()
        user_logged_out.send(
            sender=request.user.__class__, request=request, user=request.user
        )
        return Response(None, status=status.HTTP_204_NO_CONTENT)
