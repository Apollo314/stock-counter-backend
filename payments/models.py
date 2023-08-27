from django.db import models
from django.utils.translation import gettext_lazy as _

from invoice.models import Invoice
from stakeholder.models import Stakeholder
from utilities.common_model_mixins import CreateUpdateInfo, InactivatedMixin
from utilities.enums import Currency


class Bank(CreateUpdateInfo, InactivatedMixin["Bank"]):
    name = models.CharField(_("Bank name"), max_length=50, unique=True)


class PaymentAccount(CreateUpdateInfo, InactivatedMixin["PaymentAccount"]):
    name = models.CharField(_("Payment account name"), max_length=50)
    bank = models.ForeignKey(
        Bank, verbose_name=_("Bank"), on_delete=models.PROTECT, null=True, blank=True
    )
    account_number = models.CharField(_("Account number"), null=True, blank=True)
    iban = models.CharField(_("IBAN"), null=True, blank=True)
    stakeholder = models.ForeignKey(
        Stakeholder,
        verbose_name=_("Stakeholder"),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    account_currency = models.CharField(
        _("Account currency"),
        max_length=4,
        choices=Currency.choices,
        default=Currency.turkish_lira,
        blank=False,
    )
    payments_made: models.QuerySet["Payment"]
    payments_received: models.QuerySet["Payment"]

    class Meta:
        unique_together = [["name", "bank", "stakeholder"]]


class PaymentType(models.TextChoices):
    cash = "cash"
    cheque = "cheque"


class Payment(CreateUpdateInfo):
    amount = models.DecimalField(
        _("Amount"),
        max_digits=19,
        decimal_places=4,
    )
    currency = models.CharField(
        _("Currency"),
        max_length=4,
        choices=Currency.choices,
        default=Currency.turkish_lira,
    )
    payer = models.ForeignKey(
        PaymentAccount,
        verbose_name=_("Payer"),
        on_delete=models.PROTECT,
        related_name="payments_made",
    )
    receiver = models.ForeignKey(
        PaymentAccount,
        verbose_name=_("Receiver"),
        on_delete=models.PROTECT,
        related_name="payments_received",
    )
    payment_type = models.CharField(
        _("Payment type"),
        max_length=20,
        choices=PaymentType.choices,
        default=PaymentType.cash,
    )
    additional_info = models.TextField(_("Additional info"), null=True, blank=True)
    due_date = models.DateField(_("Due date"), null=True, blank=True)
    payment_done = models.BooleanField(_("Payment is concluded"), default=False)


class InvoicePayment(models.Model):
    payment = models.ForeignKey(
        Payment, verbose_name=_("Payment Info"), on_delete=models.CASCADE
    )
    invoice = models.ForeignKey(
        Invoice,
        verbose_name=_("Invoice"),
        on_delete=models.CASCADE,
        related_name="cash_payments",
    )
