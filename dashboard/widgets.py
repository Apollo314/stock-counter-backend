from abc import ABC, abstractmethod
import asyncio
from collections import defaultdict

from datetime import timedelta
from typing import Any, OrderedDict, TypeAlias
from asgiref.sync import sync_to_async
from django.db.models import QuerySet

from django.utils import timezone

from rest_framework.serializers import Serializer
from dashboard.enums import WidgetsEnum
from dashboard.serializers import InvoiceWidgetSerializer, ItemWidgetSerializer

from inventory.models import Item, StockMovement, WarehouseItemStock
from invoice.models import Invoice

from users.models import User
from users.serializers import UserSerializer

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None


class Widget(ABC):
    def __init__(self, unique_name: str, **user_inputs) -> None:
        self.user_inputs = user_inputs
        self.unique_name = unique_name

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

    def filter(self, user_inputs: dict[str, Any]):
        print(user_inputs)
        pass

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

    def get_serializer_class(self) -> Serializer:
        return InvoiceWidgetSerializer

    def get_queryset(self) -> QuerySet:
        return Invoice.objects.select_related("created_by", "stakeholder").all()


class LeftoverItems(Widget):
    """items that are not sold in a long time and are in stock"""

    unique_name = "leftover_items"

    def get_serializer_class(self) -> Serializer:
        return ItemWidgetSerializer

    def get_queryset(self):
        date = timezone.now() - timedelta(days=30)
        stock_movements = StockMovement.objects.select_related(
            "invoice_item__invoice"
        ).filter(invoice_item__invoice__last_payment_date__lt=date)
        warehouse_item_stocks = WarehouseItemStock.objects.filter(
            stockmovement__in=stock_movements
        )
        return (
            Item.objects.select_related("stock_unit", "category", "created_by")
            .prefetch_related("stocks")
            .filter(stocks__in=warehouse_item_stocks)
        )


class BestCustomers(Widget):
    """Most revenue generating customers"""

    def get_serializer_class(self) -> Serializer:
        return StakeholderBasicSerializer

    def get_queryset(self) -> QuerySet:
        return (
            Stakeholder.objects.filter(
                role__in=[
                    StakeholderRole.customer,
                    StakeholderRole.customer_and_supplier,
                ]
            )
            .alias(
                cash_in=Coalesce(
                    Sum(
                        "invoice__total",
                        filter=Q(invoice__invoice_type=InvoiceType.sale),
                    ),
                    Decimal(0),
                ),
                cash_out=Coalesce(
                    Sum(
                        "invoice__total",
                        filter=Q(invoice__invoice_type=InvoiceType.refund_sale),
                    ),
                    Decimal(0),
                ),
            )
            .annotate(cash_in=F("cash_in"))
            .order_by("-cash_in")
        )


class Balance:
    """Balance for one or all bank accounts"""

    unique_name = "balance"

    pass


class BalanceGraph:
    """Same as Balance but with graph"""

    unique_name = "balance_graph"

    pass


class LastUsers(Widget):
    unique_name = "last_users"

    def get_serializer_class(self) -> Serializer:
        return UserSerializer

    def get_queryset(self):
        return User.objects.prefetch_related("user_permissions", "groups__permissions")


class LastItems(Widget):
    unique_name = "last_items"

    def get_serializer_class(self) -> Serializer:
        return ItemWidgetSerializer

    def get_queryset(self):
        return (
            Item.objects.select_related("stock_unit", "category", "created_by")
            .prefetch_related("stocks")
            .all()
        )


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


WIDGETMAP = {
    WidgetsEnum.leftover_items: LeftoverItems,
    WidgetsEnum.last_items: LastItems,
    WidgetsEnum.last_invoices: LastInvoices,
    WidgetsEnum.due_payments: DuePayments,
    WidgetsEnum.best_customers: BestCustomers,
    WidgetsEnum.balance: Balance,
    WidgetsEnum.balange_graph: BalanceGraph,
    WidgetsEnum.last_users: LastUsers,
}
