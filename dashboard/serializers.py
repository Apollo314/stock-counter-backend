from inventory.serializers import (
    CategorySerializer,
    ItemInSerializer,
    StockUnitSerializer,
)
from stakeholder.serializers import StakeholderBasicSerializer
from users.serializers import ConciseUserSerializer
from django.utils.translation import gettext_lazy as _
from inventory import models as inventory_models
from invoice import models as invoice_models
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
