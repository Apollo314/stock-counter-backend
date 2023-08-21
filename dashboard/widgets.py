from abc import ABC, abstractmethod
import asyncio
from collections import defaultdict
from datetime import timedelta
from typing import Any, OrderedDict, TypeAlias
from asgiref.sync import sync_to_async
from django.db.models import (
    Prefetch,
    QuerySet,
)
from django.utils import timezone

from rest_framework.serializers import Serializer
from inventory.models import Item, StockMovement, WarehouseItemStock
from inventory.serializers import ItemOutSerializer
from invoice.models import Invoice

from invoice.serializers import InvoiceDetailOutSerializer
from users.models import User
from users.serializers import UserSerializer

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None


class Widget(ABC):
    _unique_name: str  # will be used for enum definition
    prefetch: Prefetch  # the query that will be prefetched

    def __init__(self, **user_inputs) -> None:
        self.user_inputs = user_inputs

    @property
    def unique_name(self) -> str:
        inputs = dict(sorted(self.user_inputs.items()))
        return (
            f"{self._unique_name}-"
            f"{'|'.join(map(lambda x:f'{x[0]}:{str(x[1])}', inputs.items()))}"
        )

    @abstractmethod
    def get_serializer_class(self) -> Serializer:
        raise NotImplementedError(
            "Subclasses must implement get_serializer_class method"
        )

    @abstractmethod
    def get_queryset(self) -> QuerySet:
        raise NotImplementedError(
            "Subclasses must implement get_serializer_class method"
        )

    def serialized_data(self, serializer_data: Any) -> JSON:
        """serialized data, should return json serializable object"""
        if isinstance(serializer_data, list):
            serializer = self.get_serializer_class()(data=serializer_data, many=True)
            serializer.is_valid()
        else:
            serializer = self.get_serializer_class()(data=serializer_data)
            serializer.is_valid()
        return serializer.data


class DuePayments:  # (Widget):
    """Payments that are needed to be made or received"""

    unique_name = "due_payments"


class LastInvoices(Widget):
    """Last created Invoices"""

    unique_name = "last_invoices"

    def get_serializer_class(self) -> Serializer:
        return InvoiceDetailOutSerializer

    def get_queryset(self) -> QuerySet:
        return Invoice.objects.all()


class LeftoverItems(Widget):
    """items that are not sold in a long time and are in stock"""

    unique_name = "leftover_items"

    def get_serializer_class(self) -> Serializer:
        return ItemOutSerializer

    def get_queryset(self):
        date = timezone.now() - timedelta(days=30)
        stock_movements = StockMovement.objects.select_related(
            "invoice_item__invoice"
        ).filter(invoice_item__invoice__last_payment_date__lt=date)
        warehouse_item_stocks = WarehouseItemStock.objects.filter(
            stockmovement__in=stock_movements
        )
        return Item.objects.filter(stocks__in=warehouse_item_stocks)


class BestCustomers:
    """Most revenue generating customers"""

    unique_name = "best_customers"

    pass


class Balance:
    """Balance for one or all bank accounts"""

    unique_name = "balance"

    pass


class BalanceGraph:
    """Same as Balance but with graph"""

    unique_name = "balance_graph"

    pass


subscribed_widgets = ["due_payments", ""]


class LastUsers(Widget):
    unique_name = "last_users"

    def get_serializer_class(self) -> Serializer:
        return UserSerializer

    def get_queryset(self):
        return User.objects.prefetch_related("user_permissions", "groups__permissions")


class LastItems(Widget):
    unique_name = "last_items"

    def get_serializer_class(self) -> Serializer:
        return ItemOutSerializer

    def get_queryset(self):
        return Item.objects.all()


async def gather_widgets_data(*widgets: Widget) -> dict[str, list[OrderedDict]]:
    """takes widgets, asyncronously queries their querysets, returns them in a dict
    with the unique_name of the widget as the key"""

    result = defaultdict(list)

    async def task(widget: Widget):
        queryset = widget.get_queryset()
        instances = []
        async for instance in queryset:
            instances.append(instance)
        result[widget.unique_name] = await sync_to_async(widget.serialized_data)(
            instances
        )

    await asyncio.gather(*(task(widget) for widget in widgets))
    return result
