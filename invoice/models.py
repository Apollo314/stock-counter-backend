from datetime import datetime, timedelta
from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from inventory.models import Item, StockMovement, Warehouse
from stakeholder.models import Stakeholder
from utilities.common_model_mixins import CreateUpdateInfo
from utilities.enums import Currency, InvoiceType


def week_from_now():
    now = timezone.now()
    return now + timedelta(weeks=1)


class Invoice(CreateUpdateInfo):
    """Satış, Alış ya da iade faturası"""

    invoice_type: InvoiceType = models.CharField(
        _("Invoice type"), max_length=20, choices=InvoiceType.choices
    )
    name: str = models.CharField("Fatura Adı", max_length=100)
    description: str = models.TextField("Açıklama", null=True, blank=True)
    invoice_conditions = models.TextField("Fatura Koşulları", null=True, blank=True)
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
        related_name=_("Invoices"),
        verbose_name=_("Depot"),
    )

    items: models.QuerySet["InvoiceItem"]

    related_invoice = models.ManyToManyField(
        "self",
        verbose_name=_("Related invoices"),
        related_name=_("Refund invoice"),
        blank=True,
        symmetrical=False,
    )

    def __str__(self):
        return "{invoice} - {self.name[:40]} - {self.created_at}".format(
            {"invoice": _("Invoice")}
        )

    class Meta:
        permissions = [("view_all_invoices", _("View all invoices"))]


class InvoiceItem(models.Model):
    invoice: Invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        verbose_name="Alakalı Fatura",
        related_name="items",
    )
    stock_movement: StockMovement = models.OneToOneField(
        StockMovement,
        on_delete=models.PROTECT,
        verbose_name=_("Stock movement"),
        related_name=_("Invoice item"),
    )
    price: Decimal = models.DecimalField(_("Price"), max_digits=19, decimal_places=4)

    def __str__(self):
        return f"{self.invoice}: {self.stock_movement}"
