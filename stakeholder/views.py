from utilities.filters import DjangoFilterBackend, OrderingFilter, SearchFilter
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet

from stakeholder import models, serializers


class SupplierViewset(ModelViewSet):
    queryset = models.Stakeholder.supplier.prefetch_related("employees").all()
    serializer_class = serializers.StakeholderSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = [
        "name",
        "phone",
        "email",
        "vkntckn",
    ]
    filterset_fields = {
        "shortname": {
            "icontains": {
                "component": "text-input",
                "props": {"label": "Kısa Adı"},
            }
        },
        "vkntckn": {
            "icontains": {
                "component": "text-input",
                "props": {"label": "VKN/TCKN"},
            }
        },
        "email": {
            "icontains": {"component": "text-input", "props": {"label": "E-Posta"}}
        },
        "phone": {
            "icontains": {"component": "text-input", "props": {"label": "Telefon"}}
        },
    }


class CustomerViewset(ModelViewSet):
    queryset = models.Stakeholder.customer.prefetch_related("employees").all()
    serializer_class = serializers.StakeholderSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = [
        "name",
        "phone",
        "email",
        "vkntckn",
    ]
    filterset_fields = {
        "shortname": {
            "icontains": {
                "component": "text-input",
                "props": {"label": "Kısa Adı"},
            }
        },
        "vkntckn": {
            "icontains": {
                "component": "text-input",
                "props": {"label": "VKN/TCKN"},
            }
        },
        "email": {
            "icontains": {"component": "text-input", "props": {"label": "E-Posta"}}
        },
        "phone": {
            "icontains": {"component": "text-input", "props": {"label": "Telefon"}}
        },
    }


class StakeholderEmployeeViewset(ModelViewSet):
    queryset = models.StakeholderEmployee.objects.all()
    serializer_class = serializers.StakeholderEmployeeSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["name", "phone", "email"]
    # filterset_fields = ["position", "email", "phone"]
