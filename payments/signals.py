from django.db.models.signals import post_delete
from django.dispatch import receiver

from payments.models import InvoicePayment


@receiver(post_delete, sender=InvoicePayment)
def delete_payment_of_invoice_payment(sender, instance: InvoicePayment, **kwargs):
    instance.payment.delete()
