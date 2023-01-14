from django.db.models import QuerySet
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from inventory import models
from inventory import serializers as inventory_serializers
from utilities.filters import DjangoFilterBackend, OrderingFilter, SearchFilter


class CategoryViewset(ModelViewSet):
    lookup_field = "name"
    # queryset = models.Category.objects.prefetch_related(
    #     "children", "children__children", "children__children__children"
    # ).all()
    queryset = models.Category.objects.all()
    serializer_class = inventory_serializers.CategorySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = ["id", "name"]
    ordering = ["-id"]
    search_fields = [
        "name",
        # "children__name",
        # "children__children__name",
        # "children__children__children__name",
    ]


class StockUnitViewset(ModelViewSet):
    lookup_field = "name"
    queryset = models.StockUnit.objects.all()
    serializer_class = inventory_serializers.StockUnitSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = ["id", "name"]
    ordering = ["name"]
    search_fields = ["name"]


class ItemViewset(ModelViewSet):
    queryset = (
        models.Item.objects.select_related(
            "created_by",
            "updated_by",
            "category",
            "stock_unit",
        )
        .prefetch_related("stocks")
        .all()
    )
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = [
        "id",
        "name",
        "created_at",
        "buyprice",
        "sellprice",
        "updated_at",
        "category",
    ]
    ordering = ["-id"]
    filterset_fields = {
        "category": {
            "in": {
                "component": "multi-category-selector",
                "props": {"label": "Kategoriler"},
            },
            "isnull": {"component": "checkbox", "props": {"label": "Kategorisiz"}},
        },
        "buyprice": {
            "range": {"component": "money-range", "props": {"label": "Alış Fiyatı"}}
        },
        "sellprice": {
            "range": {"component": "money-range", "props": {"label": "Satış Fiyatı"}}
        },
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
    }
    search_fields = ["name", "description"]

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return inventory_serializers.ItemDetailSerializer
        elif self.action == "list":
            return inventory_serializers.ItemOutSerializer
        else:
            return inventory_serializers.ItemInSerializer


class WarehouseViewset(ModelViewSet):
    filter_backends = [SearchFilter]
    queryset = models.Warehouse.objects.all()
    serializer_class = inventory_serializers.WarehouseSerializer
    search_fields = ["name", "address", "phone", "plate_number"]


class WarehouseItemStockViewset(ReadOnlyModelViewSet):
    queryset = models.WarehouseItemStock.objects.all()
    serializer_class = inventory_serializers.WarehouseItemStockSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["item__name"]
    # filterset_fields = ['warehouse', 'item']


class StockMovementViewset(ModelViewSet):
    queryset = models.StockMovement.objects.all()
    serializer_class = inventory_serializers.StockMovementSerializer
    filter_backends = [SearchFilter]
    search_fields = ["warehouse_item_stock__item__name", "amount"]
