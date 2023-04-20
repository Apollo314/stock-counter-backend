from django.db.models import QuerySet
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from inventory import models
from inventory import serializers as inventory_serializers
from invoice import serializers as invoice_serializers
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
                "props": {"label": "category"},
            },
            "isnull": {
                "component": "checkbox",
                "props": {
                    "true_label": "only_categoryless",
                    "false_label": "only_categorized",
                    "indetermined_label": "with_or_without_cateogory",
                    "toggleIndeterminate": True,
                },
            },
        },
        "buyprice": {
            "range": {"component": "money-range", "props": {"label": "buyprice"}}
        },
        "sellprice": {
            "range": {"component": "money-range", "props": {"label": "sellprice"}}
        },
        "barcode": {
            "exact": {"component": "barcode-scanner", "props": {"label": "barcode"}}
        },
        "stock_unit": {
            "in": {
                "component": "multi-stockunit-selector",
                "props": {"label": "stockunit"},
            }
        },
        "created_at": {
            "range": {
                "component": "date-time-range",
                "props": {"label": "created_at"},
            }
        },
        "updated_at": {
            "range": {
                "component": "date-time-range",
                "props": {"label": "updated_at"},
            }
        },
        "created_by": {
            "exact": {
                "component": "user-select",
                "props": {"label": "created_by"},
            }
        },
        "updated_by": {
            "exact": {
                "component": "user-select",
                "props": {"label": "updated_by"},
            }
        },
        "inactivated": {
            "exact": {
                "component": "checkbox",
                "props": {
                    "label": "inactivated",
                    "toggleIndeterminate": True,
                },
            }
        },
    }
    search_fields = ["name", "description"]

    @method_decorator(cache_page(1))
    @method_decorator(vary_on_headers("Authorization"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return inventory_serializers.ItemDetailSerializer
        elif self.action == "list":
            return inventory_serializers.ItemOutSerializer
        else:
            return inventory_serializers.ItemInSerializer


class ItemHistoryViewset(ItemViewset):
    queryset = models.Item.history.select_related(
        "created_by", "updated_by", "category", "stock_unit"
    ).all()
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = [
        "id",
        "name",
        "created_at",
        "updated_at",
        "buyprice",
        "sellprice",
        "category",
    ]
    ordering = ["-id"]
    search_fields = ["name", "description"]


class WarehouseViewset(ModelViewSet):
    filter_backends = [SearchFilter]
    queryset = models.Warehouse.objects.all()
    serializer_class = inventory_serializers.WarehouseSerializer
    search_fields = ["name", "address", "phone", "plate_number"]


class WarehouseItemStockViewset(ReadOnlyModelViewSet):
    queryset = models.WarehouseItemStock.objects.all()
    serializer_class = inventory_serializers.WarehouseItemStockInfoSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["item__name"]
    # filterset_fields = ['warehouse', 'item']


class StockMovementWithoutItemViewset(ModelViewSet):
    queryset = models.StockMovement.objects.select_related(
        "invoice_item__invoice__stakeholder",
        "invoice_item__invoice__created_by",
        "warehouse_item_stock__warehouse",
    ).all()
    serializer_class = invoice_serializers.StockMovementWithoutItemSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    search_fields = ["warehouse_item_stock__item__name"]
    ordering_fields = [
        "id",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
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
        "warehouse_item_stock__item__id": {
            "exact": {"component": "item-select", "props": {"label": "item"}}
        },
    }
