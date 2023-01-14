from decimal import Decimal

from django.test import TestCase
from utilities.enums import StockMovementType

from inventory.models import (
    Currency,
    Item,
    StockMovement,
    StockUnit,
    Warehouse,
    WarehouseItemStock,
)


class TestAppModels(TestCase):
    def setUp(self):
        self.unit: StockUnit = StockUnit.objects.create(name="Adet")
        self.item: Item = Item.objects.create(
            name="test item 1",
            description="Test Description 1",
            stock_unit=self.unit,
            kdv=18,
            buyprice=Decimal("123.44"),
            buycurrency=Currency.turkish_lira,
            sellprice=Decimal("150.0"),
            sellcurrency=Currency.turkish_lira,
        )
        self.warehouse: Warehouse = Warehouse.objects.create(name="Ana Depo")
        self.warehouse2: Warehouse = Warehouse.objects.create(name="Yeni Depo")
        self.warehouse_item_stock: WarehouseItemStock = (
            WarehouseItemStock.objects.create(item=self.item, warehouse=self.warehouse)
        )
        self.warehouse_item_stock2: WarehouseItemStock = (
            WarehouseItemStock.objects.create(item=self.item, warehouse=self.warehouse2)
        )
        self.warehouse_stock_movement: StockMovement = StockMovement.objects.create(
            warehouse_item_stock=self.warehouse_item_stock,
            amount=Decimal("10.15"),
        )
        self.warehouse_stock_movement2: StockMovement = StockMovement.objects.create(
            warehouse_item_stock=self.warehouse_item_stock2,
            amount=Decimal("5"),
        )

    def test_getting_warehouse_stock_from_item_with_warehouse(self):
        warehouse_stock = self.item.stocks.get(warehouse=self.warehouse)
        self.assertEqual(warehouse_stock, self.warehouse_item_stock)

    def test_getting_warehouse_stock_from_warehouse_with_item(self):
        warehouse_stock = self.warehouse.stocks.get(item=self.item)
        self.assertEqual(warehouse_stock, self.warehouse_item_stock)

    def test_warehouse_stock_is_updated_by_stock_movement_create(self):
        current_stock = self.warehouse_item_stock.amount
        added_stock = Decimal("12.44")
        self.added_stock: StockMovement = StockMovement.objects.create(
            warehouse_item_stock=self.warehouse_item_stock,
            amount=added_stock,
        )
        self.warehouse_item_stock.refresh_from_db()
        self.assertEqual(current_stock + added_stock, self.warehouse_item_stock.amount)

    def test_movement_decreases_the_stock(self):
        current_stock = self.warehouse_item_stock.amount
        stock = Decimal("-4.5")
        self.sold_stock: StockMovement = StockMovement.objects.create(
            warehouse_item_stock=self.warehouse_item_stock,
            amount=stock,
        )
        self.warehouse_item_stock.refresh_from_db()
        self.assertEqual(current_stock + stock, self.warehouse_item_stock.amount)

    def test_warehouse_stock_is_updated_by_stock_movement_delete(self):
        added_stock: StockMovement = StockMovement.objects.create(
            warehouse_item_stock=self.warehouse_item_stock,
            amount=Decimal("14.34"),
        )
        added_stock_amount = added_stock.amount
        current_total_stock = self.warehouse_item_stock.amount
        added_stock.delete()
        self.warehouse_item_stock.refresh_from_db()
        self.assertEqual(
            current_total_stock - added_stock_amount, self.warehouse_item_stock.amount
        )

    def test_warehouse_stock_is_updated_by_stock_movement_update(self):
        current_total_stock = self.warehouse_item_stock.amount
        self.warehouse_stock_movement.amount += Decimal("5.15")
        self.warehouse_stock_movement.save()
        self.warehouse_item_stock.refresh_from_db()
        self.assertEqual(
            current_total_stock + Decimal("5.15"), self.warehouse_item_stock.amount
        )

    def test_warehouse_stock_is_updated_by_warehouse_change_on_warehouse_item_stock(
        self,
    ):
        change = self.warehouse_stock_movement2.amount
        fromWarehouseStockBefore = self.warehouse_item_stock2.amount
        toWarehouseStockBefore = self.warehouse_item_stock.amount
        self.warehouse_stock_movement2.warehouse_item_stock = self.warehouse_item_stock
        self.warehouse_stock_movement2.save()
        self.warehouse_item_stock.refresh_from_db()
        self.warehouse_item_stock2.refresh_from_db()

        self.assertEqual(
            fromWarehouseStockBefore - change, self.warehouse_item_stock2.amount
        )
        self.assertEqual(
            toWarehouseStockBefore + change, self.warehouse_item_stock.amount
        )
