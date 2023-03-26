try:
    from hmac import compare_digest
except ImportError:

    def compare_digest(a, b):
        return a == b


import binascii

from django.http import HttpRequest
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from knox.auth import TokenAuthentication
from knox.crypto import hash_token
from knox.models import AuthToken
from knox.settings import CONSTANTS, knox_settings
from knox.signals import token_expired
from rest_framework import exceptions


class TokenCookieAuthentication(TokenAuthentication):
    def authenticate(self, request: HttpRequest):
        auth_cookie = request.COOKIES.get(knox_settings.AUTH_HEADER_PREFIX)
        if not auth_cookie:
            return None
        user, auth_token = self.authenticate_credentials(auth_cookie.encode())
        return (user, auth_token)

    def authenticate_credentials(self, token):
        """
        Due to the random nature of hashing a value, this must inspect
        each auth_token individually to find the correct one.

        Tokens that have expired will be deleted and skipped
        """
        msg = _("Invalid token.")
        token = token.decode("utf-8")
        for auth_token in AuthToken.objects.select_related("user").filter(
            token_key=token[: CONSTANTS.TOKEN_KEY_LENGTH]
        ):
            try:
                digest = hash_token(token)
            except (TypeError, binascii.Error):
                raise exceptions.AuthenticationFailed(msg)
            if compare_digest(digest, auth_token.digest):
                if knox_settings.AUTO_REFRESH and auth_token.expiry:
                    self.renew_token(auth_token)
                return self.validate_user(auth_token)
        raise exceptions.AuthenticationFailed(msg)
