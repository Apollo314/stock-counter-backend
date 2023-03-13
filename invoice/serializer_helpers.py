from decimal import Decimal
from typing import TypedDict


class ItemDict(TypedDict):
    kdv: int


class WarehouseItemStockDict(TypedDict):
    # just the necessary bits
    item: ItemDict


class StockMovementDict(TypedDict):
    # just the necessary bits
    amount: Decimal
    warehouse_item_stock: WarehouseItemStockDict


class InvoiceItemDict(TypedDict):
    # just the necessary bits
    stock_movement: StockMovementDict
    price: Decimal


class InvoiceDict(TypedDict):
    currency_exchange_rate: Decimal | None
    items: list[InvoiceItemDict]
    total: Decimal
    total_with_tax: Decimal


def calculate_total(invoice: InvoiceDict):
    cer = invoice.get("currency_exchange_rate", 1)
    invoice["total_with_tax"] = sum(
        (
            item["price"]
            * item["stock_movement"]["amount"]
            * cer
            * (
                1
                + Decimal(item["stock_movement"]["warehouse_item_stock"]["item"]["kdv"])
                / 100
            )
            for item in invoice["items"]
        )
    )
    invoice["total"] = sum(
        (
            item["price"] * item["stock_movement"]["amount"] * cer
            for item in invoice["items"]
        )
    )

    return invoice
