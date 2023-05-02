from decimal import Decimal
from typing import OrderedDict

from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from django_filters.utils import verbose_field_name
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from inventory.models import WarehouseItemStock
from inventory.serializers import (StockMovementNestedSerializer,
                                   WarehouseItemStockInfoSerializer,
                                   WarehouseSerializer)
from invoice import models
from invoice.serializer_helpers import calculate_total
from stakeholder.serializers import (StakeholderBasicSerializer,
                                     StakeholderSerializer)
from users.serializers import ConciseUserSerializer
from utilities.enums import InvoiceType
from utilities.serializer_helpers import CurrentUserDefault
from utilities.serializers import DynamicFieldsModelSerializer, ModelSerializer


class InvoiceItemListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        invoice_items = [self.child.create(vd) for vd in validated_data]
        try:
            stock_movements = [item.stock_movement for item in invoice_items]
            models.StockMovement.objects.bulk_create(stock_movements)
            fake_warehouse_item_stocks = [
                WarehouseItemStock(id=sm.warehouse_item_stock_id, amount_db=None)
                for sm in stock_movements
            ]
            WarehouseItemStock.objects.bulk_update(
                fake_warehouse_item_stocks, ["amount_db"]
            )
            # warehouse_item_stock_cache_names = [
            #     generate_cache_name(
            #         WarehouseItemStock, "amount", sm.warehouse_item_stock_id
            #     )
            #     for sm in stock_movements
            # ]
            # cache.delete_many(warehouse_item_stock_cache_names)
            models.InvoiceItem.objects.bulk_create(invoice_items)

        except IntegrityError as e:
            raise ValidationError(e)

        return invoice_items

    def update(self, invoice_items, validated_data):
        invoice_items = [
            self.child.update(ii, vd) for (vd, ii) in zip(validated_data, invoice_items)
        ]
        try:
            stock_movements = [item.stock_movement for item in invoice_items]
            warehouse_item_stocks = [sm.warehouse_item_stock for sm in stock_movements]

            models.StockMovement.objects.bulk_update(
                stock_movements, {"amount", "related_movement", "warehouse_item_stock"}
            )
            WarehouseItemStock.objects.bulk_update(warehouse_item_stocks, {"amount_db"})
        except IntegrityError as e:
            raise ValidationError(e)
        # return super().update(instance, validated_data)


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
        stock_movement_data = validated_data.get("stock_movement")
        stock_movement: models.StockMovement = StockMovementNestedSerializer().update(
            instance.stock_movement, stock_movement_data
        )
        instance.stock_movement = stock_movement
        return instance

    # stock_movement_data = validated_data.pop("stock_movement")
    # StockMovementNestedSerializer().update(
    #     instance.stock_movement, stock_movement_data
    # )
    # return super().update(instance, validated_data)

    class Meta:
        model = models.InvoiceItem
        fields = ["id", "invoice", "stock_movement", "price"]
        list_serializer_class = InvoiceItemListSerializer


class InvoiceListSerializer(ModelSerializer):
    """For listview only"""

    created_by = ConciseUserSerializer(label=_("Created by"))
    updated_by = ConciseUserSerializer(label=_("Updated by"))
    warehouse = WarehouseSerializer(label=_("Depot"))
    stakeholder = StakeholderBasicSerializer(label=_("Stakeholder"))

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


class InvoiceConditionSerializerIn(ModelSerializer):
    created_by = serializers.HiddenField(default=CurrentUserDefault())
    updated_by = serializers.HiddenField(default=CurrentUserDefault())
    field_overrides = {
        "conditions": {"component": "rich-editor", "props": {"label": _("Content of the invoice condition")}},
    }

    class Meta:
        model = models.InvoiceCondition
        fields = ["id", "condition_name", "conditions", "created_by", "updated_by"]
        extra_kwargs = {
            "condition_name": {"validators": []},
        }

class InvoiceConditionWithIdSerializerIn(InvoiceConditionSerializerIn):
    id = serializers.UUIDField(required=False)


class InvoiceConditionSerializerOut(InvoiceConditionSerializerIn):
    created_by = ConciseUserSerializer(label=_("Created by"))
    updated_by = ConciseUserSerializer(label=_("Updated by"))

    class Meta:
        model = models.InvoiceCondition
        fields = [
            "id",
            "condition_name",
            "conditions",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]


class InvoiceDetailInSerializer(DynamicFieldsModelSerializer):
    # TODO: items should have an order field and they should be ordered by that
    invoice_conditions = InvoiceConditionWithIdSerializerIn(required=False)
    field_overrides = {
        "warehouse": {"component": "warehouse-selector"},
    }
    negate_map = {
        InvoiceType.purchase: False,
        InvoiceType.sale: True,
        InvoiceType.refund_purchase: True,
        InvoiceType.refund_sale: False,
    }
    created_by = serializers.HiddenField(default=CurrentUserDefault())
    updated_by = serializers.HiddenField(default=CurrentUserDefault())
    items = InvoiceItemSerializer(many=True, write_only=True)
    related_invoice = InvoiceListSerializer(required=False, many=True)

    def signed_amount(self, amount: Decimal, invoice_type: InvoiceType):
        if self.negate_map[invoice_type]:
            return -abs(amount)
        return amount

    def create(self, validated_data: OrderedDict):
        validated_data = calculate_total(validated_data)
        invoice_conditions = validated_data.pop("invoice_conditions", None)
        items_data = validated_data.pop("items")
        invoice: models.Invoice = super().create(validated_data)
        if invoice_conditions and invoice_conditions.get("id"):
            invoice.invoice_conditions_id = invoice_conditions.get("id")
        elif invoice_conditions:
            invoice_conditions = models.InvoiceCondition.objects.create(
                **invoice_conditions
            )
            invoice.invoice_conditions_id = invoice_conditions.id
            invoice.save()
        else:
            invoice.invoice_conditions = None
        warehouse = validated_data.get("warehouse")
        for item in items_data:
            item["invoice_id"] = invoice.id
            item["stock_movement"]["amount"] = self.signed_amount(
                item["stock_movement"]["amount"], validated_data["invoice_type"]
            )
            item["stock_movement"]["warehouse_item_stock"]["warehouse"] = warehouse
        InvoiceItemSerializer(many=True).create(items_data)

        return invoice

    def update(self, invoice: models.Invoice, validated_data: OrderedDict):
        validated_data = calculate_total(validated_data)
        items_data: list[OrderedDict] = validated_data.pop("items")
        warehouse = validated_data.get("warehouse")

        invoice_conditions = validated_data.pop("invoice_conditions", None)

        updated_items = []
        created_items = []

        updated_item_ids = []

        if invoice_conditions and invoice_conditions.get("id"):
            invoice.invoice_conditions_id = invoice_conditions.get("id")
        elif invoice_conditions:
            invoice_conditions = models.InvoiceCondition.objects.create(
                **invoice_conditions
            )
            invoice.invoice_conditions_id = invoice_conditions.id
        else:
            invoice.invoice_conditions = None

        for item in items_data:
            item["invoice_id"] = invoice.id  # just in case there is a new item
            item["stock_movement"]["amount"] = self.signed_amount(
                item["stock_movement"]["amount"], validated_data["invoice_type"]
            )
            # in case there is something new or warehouse has changed
            item["stock_movement"]["warehouse_item_stock"]["warehouse"] = warehouse
            if item.get("id"):
                updated_items.append(item)
                updated_item_ids.append(item.get("id"))
            else:
                created_items.append(item)

        items_to_delete = []
        for existing_item in invoice.items.all():
            if existing_item.id not in updated_item_ids:
                items_to_delete.append(existing_item.id)

        if items_to_delete:
            invoice.items.filter(id__in=items_to_delete).delete()

        if len(created_items):
            InvoiceItemSerializer(many=True).create(created_items)

        if len(updated_items):
            InvoiceItemSerializer(many=True).update(
                invoice.items.select_related(
                    "stock_movement__warehouse_item_stock"
                ).all(),
                updated_items,
            )

        invoice.warehouse = warehouse
        return super().update(invoice, validated_data)

        # all_items = instance.items.all()

        # items_to_create = [item for item in all_items if not hasattr(item, "id")]
        # items_to_update = [item for item in all_items if hasattr(item, "id")]

        # return invoice
        # items_data: list[OrderedDict] = validated_data.pop("items")
        # items_map = {item.id: item for item in instance.items.all()}
        # for item in items_data:
        #     item["stock_movement"]["amount"] = self.signed_amount(
        #         item["stock_movement"]["amount"], validated_data["invoice_type"]
        #     )
        #     if item.get("id"):
        #         InvoiceItemSerializer().update(items_map[item["id"]], item)
        #     else:
        #         InvoiceItemSerializer().create(items_data)
        # return super().update(instance, validated_data)

    class Meta:
        model = models.Invoice
        fields = [
            "id",
            "invoice_type",
            "name",
            "description",
            "last_payment_date",
            "currency",
            "currency_exchange_rate",
            "stakeholder",
            "warehouse",
            "created_by",
            "updated_by",
            "total",
            "total_with_tax",
            "items",
            "related_invoice",
            "invoice_conditions",
        ]


class InvoiceDetailOutSerializer(InvoiceDetailInSerializer):
    warehouse = WarehouseSerializer()
    stakeholder = StakeholderSerializer()
    invoice_conditions = InvoiceConditionSerializerIn(required=False)
    items = InvoiceItemSerializer(many=True)


class InvoiceDetailOutForInvoiceItemSerializer(InvoiceDetailInSerializer):
    stakeholder = StakeholderBasicSerializer()
    created_by = ConciseUserSerializer()


class InvoiceItemWithDetailedInvoiceSerializer(ModelSerializer):
    invoice = InvoiceDetailOutForInvoiceItemSerializer(
        excluded_fields=[
            "updated_by",
            "invoice_conditions",
            "warehouse",
            "items",
            "related_invoice",
        ]
    )

    class Meta:
        model = models.InvoiceItem
        fields = ["invoice", "price"]


class StockMovementWithoutItemSerializer(ModelSerializer):
    warehouse_item_stock = WarehouseItemStockInfoSerializer(excluded_fields=["item"])
    invoice_item = InvoiceItemWithDetailedInvoiceSerializer()

    class Meta:
        model = models.StockMovement
        fields = ["id", "warehouse_item_stock", "amount", "invoice_item"]
