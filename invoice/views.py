from django.db.models import Prefetch
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
    }
    serializer_class = serializers.InvoiceListSerializer
    search_fields = ["name"]

    def get_queryset(self):
        if self.action == "retrieve":
            queryset = models.Invoice.objects.prefetch_related(
                Prefetch(
                    "items",
                    queryset=models.InvoiceItem.objects.select_related(
                        "stock_movement",
                        "stock_movement__warehouse_item_stock",
                        "stock_movement__warehouse_item_stock__item",
                    ),
                )
            ).all()
        else:
            queryset = models.Invoice.objects.all()
        return queryset

    def get_serializer_class(self):
        if self.action in ["create", "update"]:
            serializer_class = serializers.InvoiceDetailInSerializer
        elif self.action == 'retrieve':
            serializer_class = serializers.InvoiceDetailOutSerializer
        else:
            serializer_class = serializers.InvoiceListSerializer
        return serializer_class


# class InvoiceItemViewset(mixins.CreateModelMixin,
#                          mixins.UpdateModelMixin,
#                          mixins.DestroyModelMixin,
#                          GenericViewSet):
#   queryset = models.InvoiceItem.objects.all()
#   serializer_class = serializers.InvoiceItemSerializer

#   def get_serializer(self, *args, **kwargs):
#     """many=True because we want to be able to create multiple instances at once"""
#     return super().get_serializer(*args, **kwargs, many=True)
