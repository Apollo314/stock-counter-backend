from django.urls import include, path, re_path
from rest_framework import routers

from inventory import views

from .bulk_urls import url_patterns

router = routers.SimpleRouter()
router.register("category", views.CategoryViewset)
router.register("stock_unit", views.StockUnitViewset)
router.register("item", views.ItemViewset)
router.register("item-history", views.ItemHistoryViewset)
router.register("warehouse", views.WarehouseViewset)
router.register("warehouse-item-stock", views.WarehouseItemStockViewset)
router.register("stock-movement", views.StockMovementViewset)

urlpatterns = [
    path("", include(router.urls)),
    path("bulk/", include(url_patterns)),
]
