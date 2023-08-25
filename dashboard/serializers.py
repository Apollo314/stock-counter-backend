from django.utils.translation import gettext_lazy as _
from rest_framework.serializers import DecimalField

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
from users.serializers import ConciseUserSerializer
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
        ]
