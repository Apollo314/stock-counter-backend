from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import *

admin.site.register(StockUnit, SimpleHistoryAdmin)

admin.site.register(Category)


class WarehouseItemStockInline(admin.StackedInline):
    model = WarehouseItemStock
    readonly_fields = ["amount"]


class ItemAdmin(SimpleHistoryAdmin):
    list_display = ("name", "buyprice", "sellprice", "created_at")
    inlines = [WarehouseItemStockInline]


admin.site.register(Item, ItemAdmin)


admin.site.register(Warehouse)


class StockMovementInline(admin.StackedInline):
    model = StockMovement
    max_num = 1
    extra = 1


class WarehouseItemStockAdmin(admin.ModelAdmin):
    readonly_fields = ["amount"]
    # inlines = [StockMovementInline]


admin.site.register(WarehouseItemStock, WarehouseItemStockAdmin)


class StockMovementAdmin(admin.ModelAdmin):
    fields = ["amount", "warehouse_item_stock"]
    list_display = ["warehouse_item_stock", "amount"]


admin.site.register(StockMovement, StockMovementAdmin)
