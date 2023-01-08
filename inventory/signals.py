from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from inventory.models import StockMovement, Item
from utilities.signals import handle_file_field_cleanup_pre_save, handle_file_pre_delete
from utilities.enums import StockMovementType

pre_save.connect(handle_file_field_cleanup_pre_save, sender=Item)
pre_delete.connect(handle_file_pre_delete, sender=Item)


@receiver(pre_save, sender=StockMovement)
def handle_warehouse_stock_movement_save(sender, instance: StockMovement, **kwargs):
    diff = instance.signed_amount
    bulk_update = False
    if instance.pk:  # if edited:
        original: StockMovement = StockMovement.objects.get(pk=instance.pk)
        if original.warehouse_item_stock == instance.warehouse_item_stock:
            diff -= original.signed_amount
        else:
            # original amount removed from original because warehouse or item is changed.
            # either way, warehouse_item_stock is a ledger for keeping amount of one item
            # in one warehouse. therefore original amount should be subtracted from it.
            original.warehouse_item_stock.amount -= original.signed_amount
            bulk_update = True
    instance.warehouse_item_stock.amount += diff
    if bulk_update:
        instance.warehouse_item_stock._meta.model._default_manager.bulk_update(
            [instance.warehouse_item_stock, original.warehouse_item_stock], ["amount"]
        )
    else:
        instance.warehouse_item_stock.save()


@receiver(pre_delete, sender=StockMovement)
def handle_warehouse_stock_movement_delete(sender, instance: StockMovement, **kwargs):
    diff = -instance.signed_amount
    instance.warehouse_item_stock.amount += diff
    instance.warehouse_item_stock.save()
