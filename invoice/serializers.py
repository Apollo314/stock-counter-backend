from decimal import Decimal
from typing import OrderedDict

from django.db import IntegrityError
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers, validators
from rest_framework.exceptions import ValidationError
from inventory.models import WarehouseItemStock

from inventory.serializers import (
    StockMovementNestedSerializer as StockMovementNestedSerializer,
)
from inventory.serializers import (
    WarehouseItemStockNestedSerializer,
    WarehouseSerializer,
)
from invoice import models
from stakeholder.serializers import StakeholderBasicSerializer, StakeholderSerializer
from utilities.enums import InvoiceType
from utilities.serializers import CreateListSerializer, ModelSerializer
from utilities.serialzier_helpers import CurrentUserDefault

from utilities.caches import generate_cache_name, cache


class InvoiceItemListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        invoice_items = [self.child.create(attrs) for attrs in validated_data]
        try:
            stock_movements = [item.stock_movement for item in invoice_items]
            models.StockMovement.objects.bulk_create(stock_movements)

            warehouse_item_stock_cache_names = [
                generate_cache_name(
                    WarehouseItemStock, "amount", sm.warehouse_item_stock_id
                )
                for sm in stock_movements
            ]
            cache.delete_many(warehouse_item_stock_cache_names)
            models.InvoiceItem.objects.bulk_create(invoice_items)

        except IntegrityError as e:
            raise ValidationError(e)

        return invoice_items


class InvoiceItemSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False)
    stock_movement = StockMovementNestedSerializer()

    # setting required=False because it will be passed by InvoiceDetailSerializer downward
    # so that client doesn't need to pass invoice to every single item.
    invoice = serializers.IntegerField(required=False, write_only=True)

    def create(self, validated_data: OrderedDict):
        stock_movement_data = validated_data.pop("stock_movement")

        stock_movement: models.StockMovement = StockMovementNestedSerializer().create(
            stock_movement_data
        )
        # return super().create(
        #     {**validated_data, "stock_movement_id": stock_movement.id}
        # )
        instance = models.InvoiceItem(**validated_data, stock_movement=stock_movement)
        return instance

    def update(self, instance: models.InvoiceItem, validated_data: OrderedDict):
        stock_movement_data = validated_data.pop("stock_movement")
        StockMovementNestedSerializer().update(
            instance.stock_movement, stock_movement_data
        )
        return super().update(instance, validated_data)

    class Meta:
        model = models.InvoiceItem
        fields = ["id", "invoice", "stock_movement", "price"]
        list_serializer_class = InvoiceItemListSerializer


class InvoiceListSerializer(ModelSerializer):
    """For listview only"""

    warehouse = WarehouseSerializer()
    stakeholder = StakeholderBasicSerializer()

    class Meta:
        model = models.Invoice
        fields = [
            "id",
            "name",
            "description",
            "last_payment_date",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "currency",
            "currency_exchange_rate",
            "total",
            "total_with_tax",
            "stakeholder",
            "warehouse",
        ]


class InvoiceDetailInSerializer(ModelSerializer):
    negate_map = {
        InvoiceType.purchase: False,
        InvoiceType.sale: True,
        InvoiceType.refund_purchase: True,
        InvoiceType.refund_sale: False,
    }
    created_by = serializers.HiddenField(default=CurrentUserDefault())
    updated_by = serializers.HiddenField(default=CurrentUserDefault())

    def signed_amount(self, amount: Decimal, invoice_type: InvoiceType):
        if self.negate_map[invoice_type]:
            return -abs(amount)
        return amount

    items = InvoiceItemSerializer(many=True, write_only=True)
    related_invoice = InvoiceListSerializer(required=False, many=True)

    def create(self, validated_data: OrderedDict):
        items_data = validated_data.pop("items")
        invoice: models.Invoice = super().create(validated_data)
        warehouse = validated_data.get("warehouse")
        for item in items_data:
            item["invoice_id"] = invoice.id
            item["stock_movement"]["amount"] = self.signed_amount(
                item["stock_movement"]["amount"], validated_data["invoice_type"]
            )
            item["stock_movement"]["warehouse_item_stock"]["warehouse"] = warehouse
        InvoiceItemSerializer(many=True).create(items_data)
        return invoice

    def update(self, instance: models.Invoice, validated_data: OrderedDict):
        items_data: list[OrderedDict] = validated_data.pop("items")
        items_map = {item.id: item for item in instance.items.all()}
        for item in items_data:
            item["stock_movement"]["amount"] = self.signed_amount(
                item["stock_movement"]["amount"], validated_data["invoice_type"]
            )
            if item.get("id"):
                InvoiceItemSerializer().update(items_map[item["id"]], item)
            else:
                InvoiceItemSerializer().create(items_data)
        return super().update(instance, validated_data)

    class Meta:
        model = models.Invoice
        fields = [
            "id",
            "invoice_type",
            "name",
            "description",
            "invoice_conditions",
            "last_payment_date",
            "currency",
            "currency_exchange_rate",
            "stakeholder",
            "warehouse",
            "created_by",
            "updated_by",
            "items",
            "related_invoice",
        ]


class InvoiceDetailOutSerializer(InvoiceDetailInSerializer):
    warehouse = WarehouseSerializer()
    stakeholder = StakeholderSerializer()
    items = InvoiceItemSerializer(many=True)
