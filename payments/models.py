from django.db import models
from django.utils.translation import gettext_lazy as _

from invoice.models import Invoice
from stakeholder.models import Stakeholder
from utilities.common_model_mixins import CreateUpdateInfo, InactivatedMixin
from utilities.enums import Currency


class Bank(CreateUpdateInfo, InactivatedMixin):
    name = models.CharField(_("Bank name"), max_length=50, unique=True)


class PaymentAccount(CreateUpdateInfo, InactivatedMixin):
    name = models.CharField(_("Payment account name"), max_length=50)
    bank = models.ForeignKey(Bank, verbose_name=_("Bank"), on_delete=models.PROTECT)
    account_number = models.CharField(_("Account number"), null=True, blank=True)
    iban = models.CharField(_("IBAN"), null=True, blank=True)
    stakeholder = models.ForeignKey(
        Stakeholder,
        verbose_name=_("Stakeholder"),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )


class Payment(CreateUpdateInfo):
    amount = models.DecimalField(
        _("Amount"),
        max_digits=19,
        decimal_places=4,
        default=None,
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


class ChequePayment(CreateUpdateInfo):
    payment = models.ForeignKey(
        Payment, verbose_name=_("Payment info"), on_delete=models.CASCADE
    )
    cheque_number = models.CharField(
        _("Cheque number"), max_length=40, null=True, blank=True
    )


class CashPayment(CreateUpdateInfo):
    payment = models.ForeignKey(
        Payment, verbose_name=_("Payment info"), on_delete=models.CASCADE
    )


class InvoiceChequePayment(models.Model):
    cheque_payment = models.ForeignKey(
        ChequePayment, verbose_name=_("Cheque Payment Info"), on_delete=models.CASCADE
    )
    invoice = models.ForeignKey(
        Invoice,
        verbose_name=_("Invoice"),
        on_delete=models.CASCADE,
        related_name="cheque_payments",
    )


class InvoiceCashPayment(models.Model):
    cash_payment = models.ForeignKey(
        CashPayment, verbose_name=_("Cash Payment Info"), on_delete=models.CASCADE
    )
    invoice = models.ForeignKey(
        Invoice,
        verbose_name=_("Invoice"),
        on_delete=models.CASCADE,
        related_name="cash_payments",
    )
