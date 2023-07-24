from rest_framework import filters
from rest_framework.viewsets import ModelViewSet

from stakeholder import models, serializers
from utilities.filters import DjangoFilterBackend, OrderingFilter, SearchFilter


class StakeholderEmployeeViewset(ModelViewSet):
    queryset = models.StakeholderEmployee.objects.all()
    serializer_class = serializers.StakeholderEmployeeSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["name", "phone", "email"]
    # filterset_fields = ["position", "email", "phone"]


class StakeholderViewset(ModelViewSet):
    queryset = models.Stakeholder.objects.all()
    serializer_class = serializers.StakeholderSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = [
        "name",
        "phone",
        "email",
        "vkntckn",
    ]
    filterset_fields = {
        "role": {"in": {"component": "hidden", "props": {}}},
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

    def get_queryset(self):
        if self.action == "retrieve":
            queryset = models.Stakeholder.objects.prefetch_related(
                "employees", "paymentaccount_set"
            )
            return queryset
        return super().get_queryset()
