from datetime import datetime, timedelta
from decimal import Decimal

from django.db import models
from django.utils import timezone

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
        "Fatura Tipi", max_length=20, choices=InvoiceType.choices
    )
    name: str = models.CharField("Fatura Adı", max_length=100)
    description: str = models.TextField("Açıklama", null=True, blank=True)
    invoice_conditions = models.TextField("Fatura Koşulları", null=True, blank=True)
    last_payment_date: datetime = models.DateTimeField(
        "Son Ödeme Tarihi", default=week_from_now
    )
    currency: Currency = models.CharField(
        "Fatura Para Birimi",
        max_length=4,
        choices=Currency.choices,
        default=Currency.turkish_lira,
    )
    currency_exchange_rate: Decimal = models.DecimalField(
        "Döviz Kuru", max_digits=19, decimal_places=4, null=True, blank=True
    )
    total: Decimal = models.DecimalField(
        "Toplam Kdv Hariç Tutar", max_digits=19, decimal_places=4, null=True, blank=True
    )
    total_with_tax: Decimal = models.DecimalField(
        "Toplam Kdv Dahil Tutar", max_digits=19, decimal_places=4, null=True, blank=True
    )

    stakeholder: Stakeholder = models.ForeignKey(
        Stakeholder, verbose_name="Alakalı Taraf", on_delete=models.PROTECT
    )

    warehouse: Warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="invoices",
        verbose_name="Alakalı Depo",
    )

    items: models.QuerySet["InvoiceItem"]

    related_invoice = models.ManyToManyField(
        "self",
        verbose_name=("Alakalı Fatura(lar)"),
        related_name="refund_invoice",
        blank=True,
        symmetrical=False,
    )

    def __str__(self):
        return f"Fatura - {self.name[:40]} - {self.created_at}"

    class Meta:
        permissions = [("view_all_invoices", "Tüm faturaları görebilir")]


class InvoiceItem(models.Model):
    invoice: Invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        verbose_name="Alakalı Fatura",
        related_name="items",
    )
    stock_movement: StockMovement = models.OneToOneField(
        StockMovement,
        on_delete=models.CASCADE,
        verbose_name="Stok Hareketi",
        related_name="invoice_item",
    )
    price: Decimal = models.DecimalField("Fiyat", max_digits=19, decimal_places=4)
