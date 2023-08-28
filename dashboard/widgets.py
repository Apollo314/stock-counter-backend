from abc import ABC, abstractmethod
from datetime import timedelta
from decimal import Decimal
from typing import Any, TypeAlias
from django.utils import timezone

from django.db.models import F, Q, QuerySet, Sum
from django.db.models.functions import Coalesce
from rest_framework.serializers import Serializer

from dashboard.enums import WidgetsEnum
from dashboard.models import SubscribedWidget
from dashboard.serializers import (
    BalanceGraphWidgetSerializer,
    BalanceWidgetSerializer,
    BestCustomerWidgetSerializer,
    InvoiceWidgetSerializer,
    ItemWidgetSerializer,
    get_balance_graph_date_ranges,
)
from inventory.models import Item, StockMovement, WarehouseItemStock
from invoice.models import Invoice
from payments.models import Payment, PaymentAccount
from payments.serializers import PaymentOutSerializer
from stakeholder.models import Stakeholder, StakeholderRole
from users.models import User
from users.serializers import UserSerializer
from utilities.enums import InvoiceType

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None


class Widget(ABC):
    def __init__(self, subscribed_widget: SubscribedWidget, **user_inputs) -> None:
        self.user_inputs = user_inputs
        self.subscribed_widget = subscribed_widget

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


class DuePayments(Widget):
    """Payments that are needed to be made or received"""

    def get_serializer_class(self) -> Serializer:
        return PaymentOutSerializer

    def get_queryset(self) -> QuerySet:
        today = timezone.now().date()
        sevendaysfromnow = today + timedelta(days=7)
        payments = (
            Payment.objects.select_related(
                "payer__stakeholder",
                "receiver__stakeholder",
                "created_by",
                "updated_by",
            )
            .filter(payment_done=False, due_date__lte=sevendaysfromnow)
            .order_by("due_date", "amount")
        )
        return payments


class LastInvoices(Widget):
    """Last created Invoices"""

    def get_serializer_class(self) -> Serializer:
        return InvoiceWidgetSerializer

    def get_queryset(self) -> QuerySet:
        return Invoice.objects.select_related("created_by", "stakeholder").all()


class LeftoverItems(Widget):
    """items that are not sold in a long time and are in stock"""

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
        return BestCustomerWidgetSerializer

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


class Balance(Widget):
    """Balance for company payment accounts"""

    def get_serializer_class(self) -> Serializer:
        return BalanceWidgetSerializer

    def get_queryset(self) -> QuerySet:
        company_accounts = (
            PaymentAccount.objects.select_related("bank")
            .filter(stakeholder=None)
            .alias(
                cash_in=Coalesce(Sum("payments_received__amount"), Decimal(0)),
                cash_out=Coalesce(Sum("payments_made__amount"), Decimal(0)),
            )
            .annotate(balance=F("cash_in") - F("cash_out"))
        )
        return company_accounts


class BalanceGraph(Widget):
    """Same as Balance but with graph"""
    unique_name = "balance_graph"

    def get_serializer_class(self) -> Serializer:
        return BalanceGraphWidgetSerializer

    def get_queryset(self) -> QuerySet:
        date_ranges = get_balance_graph_date_ranges()
        cash_ins = {}
        cash_outs = {}
        balances = {}
        first_date = None
        for i, (date1, date2) in enumerate(date_ranges):
            if i == 0:
                first_date = date1

            cash_in = Coalesce(
                Sum(
                    "payments_received__amount",
                    filter=Q(payments_received__due_date__range=[date1, date2]),
                ),
                Decimal(0),
            )
            cash_out = Coalesce(
                Sum(
                    "payments_made__amount",
                    filter=Q(payments_made__due_date__range=[date1, date2]),
                ),
                Decimal(0),
            )
            cash_in_name = f"cash_in_{i}"
            cash_out_name = f"cash_out_{i}"
            balance = F(cash_in_name) - F(cash_out_name)

            cash_ins[cash_in_name] = cash_in
            cash_outs[cash_out_name] = cash_out
            balances[f"balance_{i}"] = balance

        cash_in_before = Coalesce(
            Sum(
                "payments_received__amount",
                filter=Q(payments_received__due_date__lt=first_date),
            ),
            Decimal(0),
        )
        cash_out_before = Coalesce(
            Sum(
                "payments_made__amount",
                filter=Q(payments_received__due_date__lt=first_date),
            ),
            Decimal(0),
        )
        cash_ins["cash_in_before"] = cash_in_before
        cash_outs["cash_out_before"] = cash_out_before
        balance_before = F("cash_in_before") - F("cash_out_before")
        balances["balance_before"] = balance_before

        return (
            PaymentAccount.objects.select_related("bank")
            .filter(stakeholder=None)
            .alias(
                **cash_ins,
                **cash_outs,
            )
        ).annotate(**balances)


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
