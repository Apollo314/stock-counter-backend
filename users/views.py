from django.contrib.auth.models import Group
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from users import serializers as users_serializers
from users.models import User
from utilities.filters import DjangoFilterBackend, OrderingFilter, SearchFilter


class GroupViewset(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = users_serializers.GroupSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name"]


class UserViewset(ModelViewSet):
    queryset = User.objects.prefetch_related('groups').all()
    serializer_class = users_serializers.UserSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["first_name", "last_name", "email", "username"]
    filterset_fields = {
        "username": {
            "icontains": {
                "component": "text-input",
                "props": {"label": "Kullanıcı Adı", "placeholder": "Kullanıcı Adı"},
            }
        },
        "first_name": {
            "icontains": {
                "component": "text-input",
                "props": {"label": "İsim", "placeholder": "İsim"},
            }
        },
        "first_name": {
            "icontains": {
                "component": "text-input",
                "props": {"label": "Soy İsim", "placeholder": "Soy İsim"},
            }
        },
        "groups": {
            'in': {
                'component': 'user-group-selector',
                'props': {'label': 'Kullanıcı Grubu'}
            }
        },
        "is_staff": {
            "exact": {"component": "checkbox", "props": {"label": "Yetkili Çalışan"}}
        },
        "is_superuser": {
            "exact": {"component": "checkbox", "props": {"label": "Admin"}}
        },
        "is_active": {"exact": {"component": "checkbox", "props": {"label": "Etkin"}}},
        "date_joined": {
            "range": {
                "component": "date-time-range",
                "props": {"label": "Kayıt Tarihi"},
            }
        },
    }


class MyAccountView(GenericAPIView):
    queryset = User.objects.prefetch_related('groups').all()
    serializer_class = users_serializers.UserWithGroupDetailSerializer

    def get(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class GroupListView(ListAPIView):
    queryset = Group.objects.all()
    serializer_class = users_serializers.GroupSerializer