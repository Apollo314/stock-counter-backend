from django.db.models import Prefetch
from django.utils.translation import gettext_lazy as _
from rest_framework.viewsets import ModelViewSet

from payments import models, serializers
from utilities.filters import DjangoFilterBackend, OrderingFilter, SearchFilter


class BankViewset(ModelViewSet):
    queryset = models.Bank.objects.all()
    serializer_class = serializers.BankSerializer
    filter_backends = [SearchFilter]
    ordering = ["-name"]
    search_fields = [
        "name",
    ]

    def get_queryset(self):
        if self.action == "list":
            return models.Bank.objects.all().select_related("created_by", "updated_by")
        return super().get_queryset()

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.BankOutSerializer
        return serializers.BankSerializer


class PaymentAccountViewset(ModelViewSet):
    queryset = models.PaymentAccount.objects.select_related(
        "bank", "stakeholder", "created_by", "updated_by"
    ).all()
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = [
        "id",
        "name",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    ]
    ordering = ["-id"]
    filterset_fields = {
        "name": {
            "icontains": {
                "component": "text-input",
                "props": {"label": _("Account name")},
            }
        },
        "created_at": {
            "range": {
                "component": "date-time-range",
                "props": {"label": _("Created at")},
            }
        },
        "updated_at": {
            "range": {
                "component": "date-time-range",
                "props": {"label": _("Updated at")},
            }
        },
        "created_by": {
            "exact": {
                "component": "user-select",
                "props": {"label": _("Created by")},
            }
        },
        "updated_by": {
            "exact": {
                "component": "user-select",
                "props": {"label": _("Updated by")},
            }
        },
        "stakeholder": {
            "exact": {
                "component": "stakeholder-selector",
                "props": {"label": _("Stakeholder")},
            }
        },
        "account_number": {
            "contains": {
                "component": "text-input",
                "props": {"label": _("Account Number")},
            }
        },
        "bank": {
            "exact": {
                "component": "bank-selector",
                "props": {"label": _("Bank")},
            }
        },
    }
    search_fields = ["name"]

    def get_serializer_class(self):
        if self.action in ["create", "update"]:
            return serializers.PaymentAccountInSerializer
        elif self.action == "retrieve":
            return serializers.PaymentAccountOutSerializer
        else:
            return serializers.PaymentAccountOutSerializer
