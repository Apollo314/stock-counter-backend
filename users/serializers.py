from django.contrib.auth.models import Group
from rest_framework import serializers

from utilities.serializers import ModelSerializer

from .models import User


class GroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name"]


class GroupDetailSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = ("id", "name", "permissions")


class UserSerializer(ModelSerializer):
    groups = GroupSerializer(many=True, required=False)

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


class UserWithGroupDetailSerializer(UserSerializer):
    groups = GroupDetailSerializer(many=True, required=False)

