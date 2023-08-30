from django.db.models.signals import post_save
from django.dispatch import receiver
from payments.models import PaymentAccount

from stakeholder.models import Stakeholder


@receiver(post_save, sender=Stakeholder)
def create_payment_account_for_stakeholder(
    sender, instance: Stakeholder, created: bool, **kwargs
):
    if created:
        payment_account_name = f"{instance.name} (default)"
        PaymentAccount.objects.create(name=payment_account_name, stakeholder=instance)
