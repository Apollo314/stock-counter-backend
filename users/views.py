import django_filters
from django.contrib.auth.models import Group, Permission
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from users import serializers as users_serializers
from users.models import User
from utilities.filters import DjangoFilterBackend, OrderingFilter, SearchFilter


class PermissionListView(ListAPIView):
    queryset = Permission.objects.all()
    serializer_class = users_serializers.PermissionSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name", "codename"]


class GroupViewset(ModelViewSet):
    queryset = Group.objects.prefetch_related("permissions__content_type").all()
    serializer_class = users_serializers.GroupSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name", "permissions__name"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return users_serializers.GroupDetailSerializer
        return users_serializers.GroupSerializer


class UserFilter(django_filters.FilterSet):
    groups__in = django_filters.filters.ModelMultipleChoiceFilter(
        field_name="groups",
        queryset=Group.objects.all(),
    )

    class Meta:
        model = User
        fields = {
            "username": {
                "icontains": {
                    "component": "text-input",
                    "props": {"label": _("username"), "placeholder": _("username")},
                }
            },
            "first_name": {
                "icontains": {
                    "component": "text-input",
                    "props": {"label": _("first name"), "placeholder": _("first name")},
                }
            },
            "last_name": {
                "icontains": {
                    "component": "text-input",
                    "props": {"label": _("last name"), "placeholder": _("last name")},
                }
            },
            "is_staff": {
                "exact": {
                    "component": "checkbox",
                    "props": {"label": _("staff status"), "toggleIndeterminate": True},
                }
            },
            "is_superuser": {
                "exact": {
                    "component": "checkbox",
                    "props": {
                        "label": _("superuser status"),
                        "toggleIndeterminate": True,
                    },
                }
            },
            "is_active": {
                "exact": {
                    "component": "checkbox",
                    "props": {"label": _("active"), "toggleIndeterminate": True},
                }
            },
            "date_joined": {
                "range": {
                    "component": "date-time-range",
                    "props": {"label": _("date joined")},
                }
            },
        }


class UserViewset(ModelViewSet):
    queryset = User.objects.prefetch_related("groups").all()
    serializer_class = users_serializers.UserSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["first_name", "last_name", "email", "username"]
    filterset_class = UserFilter
    filterset_overrides = {
        "groups": {
            "in": {
                "component": "group-selector",
                "props": {"label": _("groups"), "multiple": True},
            }
        }
    }

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return users_serializers.UserSerializer
        elif self.action == "create":
            return users_serializers.UserCreateSerializer
        elif self.action == "update":
            return users_serializers.UserUpdateSerializer
        return users_serializers.ConciseUserSerializer


class MyAccountView(GenericAPIView):
    queryset = User.objects.prefetch_related("groups").all()
    serializer_class = users_serializers.UserWithGroupDetailSerializer

    def get(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)
