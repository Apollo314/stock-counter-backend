from decimal import Decimal
from pathlib import Path
from typing import Any, List, Optional

from django.core.cache import cache
from django.db import models
from django.db.models import QuerySet
from django.db.models.aggregates import Sum
from django.db.models.expressions import Q
from django.forms import DecimalField
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from utilities.caches import persistent_cached_property
from utilities.common_model_mixins import CreateUpdateInfo, InactivatedMixin
from utilities.enums import KDV, Currency, StockMovementType
from utilities.validators import not_zero_validator


class Category(models.Model):
    name: str = models.CharField(_("Category"), unique=True, max_length=40)
    parent: "Category" = models.ForeignKey(
        "self",
        verbose_name=("Üst Kategori"),
        related_name="children",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )


class StockUnit(models.Model):
    name: str = models.CharField(_("Stock unit"), unique=True, max_length=20)

    def __str__(self):
        return self.name


# TODO: implement arbitrary tax instead of just kdv, since that is what governments do.
class Tax(models.Model):
    name: str = models.CharField("db.inventory.tax.name", max_length=40, unique=True)


def get_item_image_location(instance: "Item", filename: str):
    f = Path(filename)
    path = Path("item_images") / f"{instance.name}_{instance.id}{f.suffix}"
    return path


class Item(CreateUpdateInfo, InactivatedMixin):
    name: str = models.CharField(_("Item/Service"), max_length=200, unique=True)
    description: str = models.CharField(
        _("Description"), max_length=2000, null=True, blank=True
    )

    # buyprice including taxes.
    buyprice: Decimal = models.DecimalField(
        _("Buy price"), max_digits=19, decimal_places=4
    )
    buycurrency: Currency = models.CharField(
        _("Buy currency"),
        max_length=4,
        choices=Currency.choices,
        default=Currency.turkish_lira,
    )

    # sellprice including taxes.
    sellprice: Decimal = models.DecimalField(
        _("Sell price"), max_digits=19, decimal_places=4
    )
    sellcurrency: Currency = models.CharField(
        _("Sell currency"),
        max_length=4,
        choices=Currency.choices,
        default=Currency.turkish_lira,
        blank=False,
    )
    barcode: str = models.CharField(
        _("Barcode"), max_length=20, null=True, blank=True, unique=True
    )
    stock_code: str = models.CharField(
        _("Stock code"), max_length=40, null=True, blank=True
    )
    kdv: KDV = models.IntegerField("Katma Değer Vergisi", choices=KDV.choices)

    thumbnail: models.ImageField = models.ImageField(
        _("Thumbnail"), upload_to=get_item_image_location, null=True, blank=True
    )

    category: Category = models.ForeignKey(
        Category,
        verbose_name=_("Category"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    stock_unit: StockUnit = models.ForeignKey(
        StockUnit,
        verbose_name=_("Stock unit"),
        on_delete=models.PROTECT,
    )

    history = HistoricalRecords()

    stocks: QuerySet["WarehouseItemStock"]  # reverse foreign key

    def __str__(self):
        return f"{self.name}"


class ItemImage(models.Model):
    item: Item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="images"
    )
    image: models.ImageField = models.ImageField(
        _("Item/Service image"),
        upload_to=get_item_image_location,
    )
    description: str = models.TextField("Açıklama", null=True, blank=True)


class Warehouse(models.Model):
    name: str = models.CharField(_("Depot name"), max_length=100)
    address: str = models.CharField(_("Address"), null=True, blank=True, max_length=200)
    phone: str = models.CharField(_("Phone"), null=True, blank=True, max_length=20)
    plate_number: str = models.CharField(
        _("Plate number"), null=True, blank=True, max_length=20
    )
    stocks: QuerySet["WarehouseItemStock"]  # reverse foreign key

    def __str__(self):
        return f"{self.name}"


class WarehouseItemStock(models.Model):
    item: Item = models.ForeignKey(
        Item,
        verbose_name=_("Item/Service"),
        on_delete=models.CASCADE,
        related_name="stocks",
    )
    warehouse: Warehouse = models.ForeignKey(
        Warehouse,
        verbose_name=_("Depot name"),
        on_delete=models.PROTECT,
        null=True,
        related_name="stocks",
    )  # probably dangerous if it was CASCADE
    amount_db: models.DecimalField = models.DecimalField(
        _("Amount"), max_digits=19, decimal_places=4, default=None, null=True, blank=True
    )

    @staticmethod
    def update_stocks(ids: list[int]):
        warehouse_item_stocks = WarehouseItemStock.objects.filter(ids)
        for wis in warehouse_item_stocks:
            wis.amount_db = None
        WarehouseItemStock.objects.bulk_update(
            warehouse_item_stocks, fields=["amount_db"]
        )

    def calculate_stock(self) -> Decimal:
        stock_movements = self.stockmovement_set.all()
        agg_sum = stock_movements.aggregate(Sum("amount"))
        return Decimal(agg_sum["amount__sum"] or 0)

    # @persistent_cached_property(timeout=None)
    @property
    def amount(self) -> Decimal:
        if self.amount_db == None:
            self.amount_db = self.calculate_stock()
            self.save()
        return self.amount_db

    def refresh_from_db(
        self, using: Optional[str] = None, fields: Optional[List[str]] = None
    ) -> None:
        try:
            self.amount_db = self.calculate_stock()
            self.save()
        except:
            pass
        return super().refresh_from_db(using, fields)

    class Meta:
        unique_together = [["item", "warehouse"]]

    def __str__(self):
        return f"{self.warehouse} [{self.item}]"


class StockMovement(CreateUpdateInfo):
    warehouse_item_stock: WarehouseItemStock = models.ForeignKey(
        WarehouseItemStock, verbose_name="Stok", on_delete=models.CASCADE
    )
    amount: Decimal = models.DecimalField(
        "Miktar",
        max_digits=19,
        decimal_places=4,
        validators=[not_zero_validator],
    )
    # if moving from one warehouse to another, this will not be null,
    # while selling, or purchasing, etc. it will be null.
    related_movement: "StockMovement" = models.OneToOneField(
        "self", on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        direction = "> >" if self.amount > 0 else "< <"
        if self.related_movement:
            return f"{self.related_movement.warehouse_item_stock} {direction} {abs(self.amount)} {direction} {self.warehouse_item_stock}"
        else:
            return f"{abs(self.amount)} {direction} {self.warehouse_item_stock}"
