from django.db.models.signals import post_delete, post_save, pre_delete, pre_save
from django.dispatch import receiver

from inventory.models import Item, StockMovement
from utilities.signals import handle_file_pre_delete, handle_file_field_cleanup_pre_save

pre_save.connect(handle_file_field_cleanup_pre_save, sender=Item)
pre_delete.connect(handle_file_pre_delete, sender=Item)


# this won't be called when doing bulk create, bulk update but hey.
# doesn't hurt to have it.
@receiver(post_save, sender=StockMovement)
@receiver(post_delete, sender=StockMovement)
def clear_warehouse_item_stock_cache(sender, instance: StockMovement, **kwargs):
    if instance.warehouse_item_stock.amount_db is not None:
        instance.warehouse_item_stock.amount_db = None
        instance.warehouse_item_stock.save()
