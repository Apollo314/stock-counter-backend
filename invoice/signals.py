from django.db.models.signals import post_delete
from django.dispatch import receiver

from invoice.models import Invoice, InvoiceItem


@receiver(post_delete, sender=InvoiceItem)
def auto_delete_stock_movement_related_to_invoice_item(
    sender, instance: InvoiceItem, **kwargs
):
    instance.stock_movement.delete()
