from django.db.models import Prefetch
from django.utils.translation import gettext_lazy as _
from rest_framework.viewsets import ModelViewSet

from invoice import models, serializers
from utilities.filters import DjangoFilterBackend, OrderingFilter, SearchFilter


class InvoiceViewset(ModelViewSet):
    queryset = models.Invoice.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = [
        "id",
        "name",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "total_with_tax",
    ]
    ordering = ["-id"]
    filterset_fields = {
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
        "invoice_type": {"exact": {"component": "hidden"}},
        "items__stock_movement__warehouse_item_stock__item__id": {
            "exact": {"component": "item-select", "props": {"label": "item"}}
        },
    }
    serializer_class = serializers.InvoiceListSerializer
    search_fields = ["name"]

    def get_queryset(self):
        if self.action == "retrieve":
            queryset = (
                models.Invoice.objects.select_related(
                    "created_by",
                    "updated_by",
                    "warehouse",
                    "stakeholder",
                    "invoice_condition__invoice_condition_template",
                )
                .prefetch_related(
                    Prefetch(
                        "items",
                        queryset=models.InvoiceItem.objects.select_related(
                            "stock_movement",
                            "stock_movement__warehouse_item_stock",
                            "stock_movement__warehouse_item_stock__item",
                        ),
                    ),
                )
                .all()
            )
        else:
            queryset = models.Invoice.objects.select_related(
                "created_by",
                "updated_by",
                "warehouse",
                "stakeholder",
                "invoice_condition__invoice_condition_template",
            ).all()
        return queryset

    def get_serializer_class(self):
        if self.action in ["create", "update"]:
            serializer_class = serializers.InvoiceDetailInSerializer
        elif self.action == "retrieve":
            serializer_class = serializers.InvoiceDetailOutSerializer
        else:
            serializer_class = serializers.InvoiceListSerializer
        return serializer_class


class InvoiceConditionTemplateViewset(ModelViewSet):
    queryset = models.InvoiceConditionTemplate.objects.select_related(
        "created_by", "updated_by"
    ).all()
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = [
        "condition_name",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    ]
    ordering = ["-created_at"]
    filterset_fields = {
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
        "condition_name": {"icontains": {"component": "hidden", "props": {}}},
        "conditions": {
            "icontains": {"component": "text-input", "props": {"label": _("Contents")}}
        },
    }
    search_fields = ["condition_name"]

    def get_serializer_class(self):
        if self.action in ["create", "update"]:
            serializer_class = serializers.InvoiceConditionTemplateInSerializer
        else:
            serializer_class = serializers.InvoiceConditionTemplateOutSerializer
        return serializer_class
