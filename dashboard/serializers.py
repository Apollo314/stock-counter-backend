from datetime import timedelta

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import PolymorphicProxySerializer, extend_schema_field
from rest_framework.renderers import serializers
from rest_framework.serializers import (
    CharField,
    DateField,
    DecimalField,
    IntegerField,
    JSONField,
    ListField,
    SerializerMethodField,
)

from inventory import models as inventory_models
from inventory.serializers import (
    CategorySerializer,
    ItemInSerializer,
    StockUnitSerializer,
)
from invoice import models as invoice_models
from payments.models import PaymentAccount
from payments.serializers import BankSerializer
from stakeholder.models import Stakeholder
from stakeholder.serializers import StakeholderBasicSerializer
from users.serializers import ConciseUserSerializer, UserSerializer
from utilities.serializers import ModelSerializer


class ItemWidgetSerializer(ItemInSerializer):
    stock_unit = StockUnitSerializer(label=_("Stock unit"))
    created_by = ConciseUserSerializer(label=_("Created by"))
    category = CategorySerializer(required=False, label=_("Category"))

    class Meta:
        model = inventory_models.Item
        fields = [
            "id",
            "name",
            "thumbnail",
            "stock_unit",
            "stocks",
            "buyprice",
            "sellprice",
            "buycurrency",
            "sellcurrency",
            "created_by",
            "category",
        ]


class InvoiceWidgetSerializer(ModelSerializer):
    stakeholder = StakeholderBasicSerializer()
    created_by = ConciseUserSerializer(label=_("Created by"))

    class Meta:
        model = invoice_models.Invoice
        fields = [
            "id",
            "invoice_type",
            "name",
            "description",
            "last_payment_date",
            "currency",
            "currency_exchange_rate",
            "stakeholder",
            "created_by",
            "total",
            "total_with_tax",
        ]


class BestCustomerWidgetSerializer(ModelSerializer):
    cash_in = DecimalField(max_digits=19, decimal_places=4)

    class Meta:
        model = Stakeholder
        fields = [
            "id",
            "name",
            "role",
            "shortname",
            "phone",
            "email",
            "vkntckn",
            "address",
            "cash_in",
        ]


class BalanceWidgetSerializer(ModelSerializer):
    bank = BankSerializer()
    balance = DecimalField(max_digits=19, decimal_places=4)

    class Meta:
        model = PaymentAccount
        fields = [
            "id",
            "name",
            "bank",
            "account_number",
            "iban",
            "balance",
            "account_currency"
        ]


def get_balance_graph_date_ranges():
    today = timezone.now().date()
    dates = [today + timedelta(days=i) for i in range(-20, 20)]
    return zip(dates, dates)


class BalancesSerializer(serializers.Serializer):
    """this exist to fill openapi schema correctly. no other reason"""

    balance = DecimalField(19, 4)
    range = ListField(child=DateField(), min_length=2, max_length=2)


class BalanceGraphWidgetSerializer(ModelSerializer):
    bank = BankSerializer()
    balances = serializers.SerializerMethodField()

    @extend_schema_field(BalancesSerializer(many=True))
    def get_balances(self, obj):
        date_ranges = list(get_balance_graph_date_ranges())
        balance_names = [f"balance_{i}" for i in range(len(date_ranges))]
        balances = [
            {"balance": getattr(obj, name), "range": date_range}
            for name, date_range in zip(balance_names, date_ranges)
        ]
        return balances

    class Meta:
        model = PaymentAccount
        fields = [
            "id",
            "name",
            "bank",
            "account_number",
            "iban",
            "balances",
            "account_currency",
        ]


class DashboardSerializer(serializers.Serializer):
    """This doesn't really do anything other than hinting openapi."""

    id = IntegerField()
    widget_index = IntegerField()
    user_settings = JSONField()
    widget_name = CharField()
    widget_data = SerializerMethodField()

    @extend_schema_field(
        PolymorphicProxySerializer(
            component_name="widget_data",
            serializers=[
                ItemWidgetSerializer,
                InvoiceWidgetSerializer,
                BestCustomerWidgetSerializer,
                BalanceWidgetSerializer,
                BalanceGraphWidgetSerializer,
                UserSerializer,
            ],
            resource_type_field_name="type",
        )
    )
    def get_widget_data(self, obj):
        pass
