from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer
from users.serializers import UserSerializer


class LoginSerializer(AuthTokenSerializer):
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
                msg = "Verilen bilgilerle giriş yapılamadı. Kontrol ederek yeniden giriniz."
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
