from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer

from users.serializers import UserSerializer


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(label=_("Username"), write_only=True)
    password = serializers.CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    user = UserSerializer(read_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            user = authenticate(
                request=self.context.get("request"),
                username=username,
                password=password,
            )

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _(
                    "Couldn't login with the given information. Password or Username may be wrong."
                )
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = "Kullanıcı adı ve şifre girilmeli."
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    digest = serializers.CharField(
        label="Token digest", write_only=True, required=False
    )


class LogoutAllSerializer(serializers.Serializer):
    pass
