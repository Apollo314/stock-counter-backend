import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from inventory.models import StockMovement, Warehouse
from stakeholder.models import Stakeholder
from utilities.common_model_mixins import CreateUpdateInfo
from utilities.enums import Currency, InvoiceType


class InvoiceConditionTemplate(CreateUpdateInfo):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conditions: str = models.TextField(_("Invoice conditions"))
    condition_name: str = models.CharField(
        _("Condition identifier name (ex: Default conditions)"),
        unique=True,
        max_length=100,
    )


def week_from_now():
    now = timezone.now()
    return now + timedelta(weeks=1)


class Invoice(CreateUpdateInfo):
    invoice_type: InvoiceType = models.CharField(
        _("Invoice type"), max_length=20, choices=InvoiceType.choices
    )
    name: str = models.CharField(_("Invoice name"), max_length=100)
    description: str = models.TextField(_("Description"), null=True, blank=True)
    last_payment_date: datetime = models.DateTimeField(
        _("Last payment date"), default=week_from_now
    )
    currency: Currency = models.CharField(
        _("Invoice currency"),
        max_length=4,
        choices=Currency.choices,
        default=Currency.turkish_lira,
    )
    currency_exchange_rate: Decimal = models.DecimalField(
        _("Currency exchange rate"),
        max_digits=19,
        decimal_places=4,
        null=True,
        blank=True,
    )
    total: Decimal = models.DecimalField(
        _("Total without tax"), max_digits=19, decimal_places=4, null=True, blank=True
    )
    total_with_tax: Decimal = models.DecimalField(
        _("Total with tax"), max_digits=19, decimal_places=4, null=True, blank=True
    )

    stakeholder: Stakeholder = models.ForeignKey(
        Stakeholder, verbose_name=_("Stakeholder"), on_delete=models.PROTECT
    )

    warehouse: Warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="invoices",
        verbose_name=_("Depot"),
    )

    cash_payments: models.QuerySet["InvoiceCashPayment"]
    cheque_payments: models.QuerySet["InvoiceChequePayment"]
    items: models.QuerySet["InvoiceItem"]
    invoice_condition: models.QuerySet["InvoiceCondition"]

    related_invoice = models.ManyToManyField(
        "self",
        verbose_name=_("Related invoices"),
        related_name="refund_invoice",
        blank=True,
        symmetrical=False,
    )

    def __str__(self):
        return f"Fatura - {self.name[:40]} - {self.created_at}"

    class Meta:
        permissions = [("view_all_invoices", _("Can view all invoices"))]


class InvoiceCondition(models.Model):
    """A copy of InvoiceConditionTemplate for a specific invoice.
    it exists so that even if InvoiceConditionTemplate is changed, a permenant copy of it
    persists for an invoice."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    invoice_condition_template: InvoiceConditionTemplate = models.ForeignKey(
        InvoiceConditionTemplate,
        on_delete=models.SET_NULL,
        verbose_name=_("Invoice Condition Template"),
        related_name="invoice_conditions",
        null=True,
        blank=True,
    )

    invoice: Invoice = models.OneToOneField(
        Invoice,
        on_delete=models.CASCADE,
        verbose_name=_("Invoice"),
        related_name="invoice_condition",
    )

    conditions: str = models.TextField(_("Invoice conditions"))


class InvoiceItem(models.Model):
    invoice: Invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        verbose_name=_("Related Invoice"),
        related_name="items",
    )
    stock_movement: StockMovement = models.OneToOneField(
        StockMovement,
        on_delete=models.PROTECT,
        verbose_name=_("Stock movement"),
        related_name="invoice_item",
    )
    price: Decimal = models.DecimalField(_("Price"), max_digits=19, decimal_places=4)

    def __str__(self):
        return f"{self.invoice}: {self.stock_movement}"
