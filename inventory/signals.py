from django.db.models.signals import pre_delete, pre_save, post_save, post_delete
from django.dispatch import receiver

from inventory.models import StockMovement, Item, WarehouseItemStock
from utilities.signals import handle_file_field_cleanup_pre_save, handle_file_pre_delete
from utilities.enums import StockMovementType

pre_save.connect(handle_file_field_cleanup_pre_save, sender=Item)
pre_delete.connect(handle_file_pre_delete, sender=Item)

@receiver(post_save, sender=StockMovement)
@receiver(post_delete, sender=StockMovement)
def clear_warehouse_item_stock_cache(sender, instance: StockMovement, **kwargs):
    # setting amount to None will reset the cache
    # no need to do anything else, saving is not required.
    WarehouseItemStock(id=instance.warehouse_item_stock_id).amount = None
    # instance.warehouse_item_stock.amount = None



# this was made to keep an amount field in warehouse_item_stock sync with stock movements. but
# changed this amount field to a cached_property and just using aggregate sum for stock movement amounts

# @receiver(pre_save, sender=StockMovement)
# def handle_warehouse_stock_movement_save(sender, instance: StockMovement, **kwargs):
#     diff = instance.signed_amount
#     bulk_update = False
#     if instance.pk:  # if edited:
#         original: StockMovement = StockMovement.objects.get(pk=instance.pk)
#         if original.warehouse_item_stock == instance.warehouse_item_stock:
#             diff -= original.signed_amount
#         else:
#             # original amount removed from original because warehouse or item is changed.
#             # either way, warehouse_item_stock is a ledger for keeping amount of one item
#             # in one warehouse. therefore original amount should be subtracted from it.
#             original.warehouse_item_stock.amount -= original.signed_amount
#             bulk_update = True
#     instance.warehouse_item_stock.amount += diff
#     if bulk_update:
#         instance.warehouse_item_stock._meta.model._default_manager.bulk_update(
#             [instance.warehouse_item_stock, original.warehouse_item_stock], ["amount"]
#         )
#     else:
#         instance.warehouse_item_stock.save()


# @receiver(pre_delete, sender=StockMovement)
# def handle_warehouse_stock_movement_delete(sender, instance: StockMovement, **kwargs):
#     diff = -instance.signed_amount
#     instance.warehouse_item_stock.amount += diff
#     instance.warehouse_item_stock.save()
