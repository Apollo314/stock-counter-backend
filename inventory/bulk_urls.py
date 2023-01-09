from django.urls import path

from inventory import bulkviews

url_patterns = [
    path("item/", bulkviews.BulkItemViews.as_view()),
    path("category/", bulkviews.BulkCategoryViews.as_view()),
    path("stock-unit/", bulkviews.BulkStockUnitViews.as_view()),
    path("warehouse/", bulkviews.BulkWarehouseViews.as_view()),
]
