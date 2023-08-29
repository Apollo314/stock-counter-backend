from django.db.models.signals import post_save
from django.dispatch import receiver
from payments.models import PaymentAccount

from stakeholder.models import Stakeholder


# this won't be called when doing bulk create, bulk update but hey.
# doesn't hurt to have it.
@receiver(post_save, sender=Stakeholder)
def clear_warehouse_item_stock_cache(
    sender, instance: Stakeholder, created: bool, **kwargs
):
    if created:
        payment_account_name = f"{instance.name} (default)"
        PaymentAccount.objects.create(name=payment_account_name, stakeholder=instance)
