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
    """calculates the total of the invoice in terms of the currency of the invoice.
    ex: 1300 (USD) instead of 13000 (TRY)"""
    invoice["total_with_tax"] = Decimal(
        sum(
            (
                item["price"]
                * item["stock_movement"]["amount"]
                * (
                    1
                    + Decimal(
                        item["stock_movement"]["warehouse_item_stock"]["item"]["kdv"]
                    )
                    / 100
                )
                for item in invoice["items"]
            )
        )
    )
    invoice["total"] = Decimal(
        sum(
            (
                item["price"] * item["stock_movement"]["amount"]
                for item in invoice["items"]
            )
        )
    )

    return invoice
