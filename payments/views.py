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
            },
            "isnull": {
                "component": "checkbox",
            },
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


class PaymentViewset(ModelViewSet):
    queryset = models.Payment.objects.all()
    serializer_class = serializers.PaymentOutSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = [
        "id",
        "amount",
        "currency",
        "payer",
        "receiver",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    ]
    ordering = ["-id"]
    filterset_fields = {
        "payer": {
            "exact": {
                "component": "payment-account-select",
                "props": {"label": _("Payer")},
            }
        },
        "receiver": {
            "exact": {
                "component": "payment-account-select",
                "props": {"label": _("Receiver")},
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
        "due_date": {
            "range": {
                "component": "date-time-range",
                "props": {"label": _("Due date")},
            }
        },
        "additional_info": {
            "icontains": {
                "component": "text-input",
                "props": {"label": _("Additional info")},
            }
        },
        "payment_type": {
            "exact": {
                "component": "payment-type-select",
                "props": {"label": _("Payment type")},
            }
        },
    }
    search_fields = [
        "payer__name",
        "payer__stakeholder__name",
        "payer__iban",
        "payer__account_number" "receiver__name",
        "receiver__stakeholder__name",
        "receiver__iban",
        "receiver__account_number",
    ]


class InvoicePaymentViewset(ModelViewSet):
    queryset = models.InvoicePayment.objects.select_related("payment").all()
    serializer_class = serializers.InvoicePaymentSerializer
    filter_backends = [DjangoFilterBackend]
    ordering = ["id"]
    filterset_fields = {
        "invoice": {
            "exact": {
                "component": "invoice-select",
                "props": {"label": _("Invoice")},
            }
        },
    }
