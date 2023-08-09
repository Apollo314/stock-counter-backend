from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from utilities.serializers import ModelSerializer

from .models import User


class ContentTypeSerializer(ModelSerializer):
    class Meta:
        model = ContentType
        fields = ["id", "app_label", "model", "name"]


class PermissionSerializer(ModelSerializer):
    content_type = ContentTypeSerializer(label=_("content type"))

    class Meta:
        model = Permission
        fields = ["id", "name", "content_type", "codename"]


class GroupSerializer(ModelSerializer):
    field_overrides = {
        "permissions": {"component": "permissions-selector"},
    }

    class Meta:
        model = Group
        fields = ["id", "name", "permissions"]


class GroupDetailSerializer(ModelSerializer):
    permissions = PermissionSerializer(label=_("permissions"), many=True)

    class Meta:
        model = Group
        fields = ("id", "name", "permissions")


class UserSerializer(ModelSerializer):
    groups = GroupSerializer(many=True, required=False, label=_("groups"))

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "date_joined",
            "last_login",
            "is_active",
            "is_staff",
            "is_superuser",
            "avatar",
            "groups",
        )


class ConciseUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "date_joined",
            "last_login",
            "is_active",
            "is_staff",
            "is_superuser",
            "avatar",
            "groups",
        )


USER_FORM_OVERRIDES = {
    "groups": {"component": "group-selector"},
    "avatar": {"component": "single-image-selector"},
    "is_staff": {"component": "checkbox", "props": {"label": _("User is staff")}},
    "is_superuser": {
        "component": "checkbox",
        "props": {"label": _("User is admin")},
    },
    "password": {"component": "password-input", "props": {"suggest": True}},
    "password2": {"component": "password-input", "props": {"suggest": False}},
}


class UserUpdateSerializer(ModelSerializer):
    field_overrides = USER_FORM_OVERRIDES

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "is_staff",
            "is_superuser",
            "avatar",
            "groups",
        )


class UserCreateSerializer(ModelSerializer):
    field_overrides = USER_FORM_OVERRIDES
    password2 = serializers.CharField(
        write_only=True,
        label=_("Reenter the password"),
    )

    def save(self):
        password = self.validated_data.pop("password")
        password2 = self.validated_data.pop("password2")
        user = User(**self.validated_data)
        if password != password2:
            raise serializers.ValidationError(
                {
                    "password": _("Passwords must match."),
                    "password2": _("Passwords must match."),
                }
            )
        user.set_password(password)
        user.save()
        return user

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "is_staff",
            "is_superuser",
            "avatar",
            "groups",
            "password",
            "password2",
        )
        extra_kwargs = {"password": {"write_only": True}}


class UserWithGroupDetailSerializer(UserSerializer):
    groups = GroupDetailSerializer(many=True, required=False)
