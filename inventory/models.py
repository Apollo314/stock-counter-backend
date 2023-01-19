from decimal import Decimal
from pathlib import Path
from typing import Any, List, Optional

from django.core.cache import cache
from django.db import models
from django.db.models import QuerySet
from django.db.models.aggregates import Sum
from django.db.models.expressions import Q
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from utilities.caches import persistent_cached_property
from utilities.common_model_mixins import CreateUpdateInfo
from utilities.enums import KDV, Currency, StockMovementType
from utilities.validators import not_zero_validator


class Category(models.Model):
    name: str = models.CharField(_("Kategori"), unique=True, max_length=40)
    parent: "Category" = models.ForeignKey(
        "self",
        verbose_name=("Üst Kategori"),
        related_name="children",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )


class StockUnit(models.Model):
    name: str = models.CharField("Birim", unique=True, max_length=20)

    def __str__(self):
        return self.name


def get_item_image_location(instance: "Item", filename: str):
    f = Path(filename)
    path = Path("item_images") / f"{instance.name}_{instance.id}{f.suffix}"
    return path


class Item(CreateUpdateInfo):
    name: str = models.CharField("Ürün/Hizmet", max_length=200, unique=True)
    description: str = models.CharField(
        "Açıklama", max_length=2000, null=True, blank=True
    )

    # buyprice including taxes.
    buyprice: Decimal = models.DecimalField(
        "Alış Fiyatı", max_digits=19, decimal_places=4
    )
    buycurrency: Currency = models.CharField(
        "Alış Para Birimi",
        max_length=4,
        choices=Currency.choices,
        default=Currency.turkish_lira,
    )

    # sellprice including taxes.
    sellprice: Decimal = models.DecimalField(
        "Satış Fiyatı", max_digits=19, decimal_places=4
    )
    sellcurrency: Currency = models.CharField(
        "Satış Para Birimi",
        max_length=4,
        choices=Currency.choices,
        default=Currency.turkish_lira,
        blank=False,
    )
    barcode: str = models.CharField("Barkod", max_length=20, null=True, blank=True)
    stock_code: str = models.CharField(
        "Stok Kodu", max_length=40, null=True, blank=True
    )
    kdv: KDV = models.IntegerField("Katma Değer Vergisi", choices=KDV.choices)

    thumbnail: models.ImageField = models.ImageField(
        "Önizleme Fotoğraf", upload_to=get_item_image_location, null=True, blank=True
    )

    category: Category = models.ForeignKey(
        Category,
        verbose_name="Kategori",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    stock_unit: StockUnit = models.ForeignKey(
        StockUnit,
        verbose_name="Stok Birimi",
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
        "Ürün/Hizmet Fotoğrafı", upload_to=get_item_image_location
    )
    description: str = models.TextField("Açıklama", null=True, blank=True)


class Warehouse(models.Model):
    name: str = models.CharField("Depo adı", max_length=100)
    address: str = models.CharField(
        "Adress (varsa)", null=True, blank=True, max_length=200
    )
    phone: str = models.CharField("Telefon", null=True, blank=True, max_length=20)
    mobile: bool = models.BooleanField("Hareketli Depo(Araç)", default=False)
    plate_number: str = models.CharField(
        "Plaka (varsa)", null=True, blank=True, max_length=20
    )

    stocks: QuerySet["WarehouseItemStock"]  # reverse foreign key

    def __str__(self):
        return f"{self.name}"


class WarehouseItemStock(models.Model):
    item: Item = models.ForeignKey(
        Item, verbose_name="Ürün", on_delete=models.CASCADE, related_name="stocks"
    )
    warehouse: Warehouse = models.ForeignKey(
        Warehouse,
        verbose_name="Depo",
        on_delete=models.PROTECT,
        null=True,
        related_name="stocks",
    )  # probably dangerous if it was CASCADE

    @persistent_cached_property(timeout=None)
    def amount(self) -> Decimal:
        stock_movements = self.stockmovement_set.all()
        agg_sum = stock_movements.aggregate(Sum("amount"))
        return Decimal(agg_sum["amount__sum"] or 0)

    def refresh_from_db(
        self, using: Optional[str] = None, fields: Optional[List[str]] = None
    ) -> None:
        try:
            self.amount = None
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
