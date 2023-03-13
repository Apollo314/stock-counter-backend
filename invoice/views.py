from django.db.models import Prefetch
from django.db.models.query import QuerySet
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from rest_framework import filters, mixins
from rest_framework.viewsets import GenericViewSet, ModelViewSet

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
                "props": {"label": "Oluşturma tarihi"},
            }
        },
        "updated_at": {
            "range": {
                "component": "date-time-range",
                "props": {"label": "Güncellenme tarihi"},
            }
        },
        "created_by": {
            "exact": {
                "component": "user-select",
                "props": {"label": "Oluşturan kullanıcı"},
            }
        },
        "updated_by": {
            "exact": {
                "component": "user-select",
                "props": {"label": "Güncelleyen kullanıcı"},
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
                    "created_by", "updated_by", "warehouse", "stakeholder"
                )
                .prefetch_related(
                    Prefetch(
                        "items",
                        queryset=models.InvoiceItem.objects.select_related(
                            "stock_movement",
                            "stock_movement__warehouse_item_stock",
                            "stock_movement__warehouse_item_stock__item",
                        ),
                    )
                )
                .all()
            )
        else:
            queryset = models.Invoice.objects.select_related(
                "created_by", "updated_by", "warehouse", "stakeholder"
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
