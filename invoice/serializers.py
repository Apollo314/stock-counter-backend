from typing import OrderedDict

from django.db import IntegrityError
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers, validators
from rest_framework.exceptions import ValidationError

from inventory.serializers import (
    StockMovementNestedSerializer as StockMovementNestedSerializer_,
)
from inventory.serializers import (
    WarehouseItemStockNestedSerializer,
    WarehouseSerializer,
)
from invoice import models
from stakeholder.serializers import StakeholderSerializer
from utilities.serializers import CreateListSerializer, ModelSerializer


class StockMovementNestedSerializer(StockMovementNestedSerializer_):
    warehouse_item_stock = WarehouseItemStockNestedSerializer()
    pass


class InvoiceItemListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        invoice_items = [self.child.create(attrs) for attrs in validated_data]
        try:
            # stock_movements = [item.stock_movement for item in invoice_items]
            # models.StockMovement.objects.bulk_create(stock_movements)
            # for item in invoice_items:
            #     item.stock_movement_id = item.stock_movement.id
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
    stakeholder = StakeholderSerializer()

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
    items = InvoiceItemSerializer(many=True)
    related_invoice = InvoiceListSerializer(required=False, many=True)

    def create(self, validated_data: OrderedDict):
        items_data = validated_data.pop("items")
        invoice: models.Invoice = super().create(validated_data)
        warehouse = validated_data.get("warehouse")
        for item in items_data:
            item["invoice_id"] = invoice.id
            item["stock_movement"]["movement_type"] = validated_data["invoice_type"]
            item["stock_movement"]["warehouse_item_stock"]["warehouse"] = warehouse
        invoice.items.set(InvoiceItemSerializer(many=True).create(items_data))
        return invoice

    def update(self, instance: models.Invoice, validated_data: OrderedDict):
        items_data: list[OrderedDict] = validated_data.pop("items")
        items_map = {item.id: item for item in instance.items.all()}
        for item_data in items_data:
            if item_data.get("id"):
                InvoiceItemSerializer().update(items_map[item_data["id"]], item_data)
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
            "items",
            "related_invoice",
        ]


class InvoiceDetailOutSerializer(InvoiceDetailInSerializer):
    warehouse = WarehouseSerializer()
    stakeholder = StakeholderSerializer()
