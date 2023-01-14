from decimal import Decimal
from typing import Any, OrderedDict

from drf_extra_fields.fields import Base64ImageField
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from inventory import models
from users.serializers import ConciseUserSerializer, UserSerializer
from utilities.serializermixins import UniqueFieldsMixin
from utilities.serializers import (
    DynamicFieldsModelSerializer,
    ModelSerializer,
    UpdateListSerializer,
)
from utilities.serialzier_helpers import CurrentUserDefault


@extend_schema_serializer(
    extensions={
        "x-components": {
            "parent": {"component": "category-selector"},
        }
    }
)
class CategorySerializer(ModelSerializer):
    def validate_name(self, value):
        if not self.instance:
            qs = self.Meta.model._default_manager.filter(name__iexact=value)
            if qs.exists():
                raise serializers.ValidationError(
                    f"Kategori büyük küçük harf duyarsız şekilde eşsiz olmalı."
                )
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {**representation, "parent": CategorySerializer(instance.parent).data}

    def validate_parent(self, value):
        if self.instance == value:
            raise serializers.ValidationError("Üst kategori kategorinin kendisi olamaz")
        return value

    class Meta:
        model = models.Category
        fields = ["id", "name", "parent"]
        # extra_kwargs = {
        #   'parent': {'write_only': True}
        # }


class StockUnitSerializer(UniqueFieldsMixin, ModelSerializer):
    # id = serializers.IntegerField(required=False)

    def validate_name(self, value):
        if not self.instance:
            qs = self.Meta.model._default_manager.filter(name__iexact=value)
            if qs.exists():
                raise serializers.ValidationError(
                    f"Birim büyük küçük harf duyarsız şekilde eşsiz olmalı."
                )
        return value

    class Meta:
        model = models.StockUnit
        fields = ["id", "name"]


class WarehouseSerializer(ModelSerializer):
    class Meta:
        model = models.Warehouse
        fields = ["id", "name", "address", "phone", "mobile", "plate_number"]


class WarehouseItemStockSerializer(ModelSerializer):
    amount = serializers.DecimalField(max_digits=19, decimal_places=4, read_only=True)

    class Meta:
        model = models.WarehouseItemStock
        fields = ["id", "item", "warehouse", "amount"]


@extend_schema_serializer(
    extensions={
        "x-components": {
            "stock_unit": {"component": "unit-selector"},
            "barcode": {"component": "barcode-scanner"},
            "thumbnail": {"component": "single-image-selector"},
            "category": {"component": "category-selector"},
            "buyprice": {"component": "money-input"},
            "sellprice": {"component": "money-input"},
        }
    }
)
class ItemInSerializer(DynamicFieldsModelSerializer):
    # """For list actions like bulk update bulk delete..."""
    stocks = WarehouseItemStockSerializer(many=True, read_only=True)
    created_by = serializers.HiddenField(default=CurrentUserDefault())
    updated_by = serializers.HiddenField(default=CurrentUserDefault())

    class Meta:
        model = models.Item
        list_serializer_class = UpdateListSerializer
        fields = [
            "id",
            "name",
            "thumbnail",
            "stock_unit",
            "buyprice",
            "buycurrency",
            "sellprice",
            "sellcurrency",
            "kdv",
            "stock_code",
            "stocks",
            "barcode",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "description",
            "category",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ItemOutSerializer(ItemInSerializer):
    stock_unit = StockUnitSerializer()
    category = CategorySerializer()
    created_by = ConciseUserSerializer()
    updated_by = ConciseUserSerializer()


class ItemDetailSerializer(ItemOutSerializer):
    """For individual actions, create, update, delete..."""

    previous_id = serializers.SerializerMethodField(required=False)
    next_id = serializers.SerializerMethodField(required=False)

    def get_previous_id(self, obj) -> int:
        prev_obj = self.Meta.model.objects.filter(pk__lt=obj.pk).order_by("-pk").first()
        if prev_obj:
            return prev_obj.id

    def get_next_id(self, obj) -> int:
        next_obj = self.Meta.model.objects.filter(pk__gt=obj.pk).order_by("pk").first()
        if next_obj:
            return next_obj.id

    class Meta:
        model = models.Item
        fields = [
            "id",
            "name",
            "thumbnail",
            "stock_unit",
            "buyprice",
            "buycurrency",
            "sellprice",
            "sellcurrency",
            "kdv",
            "stock_code",
            "stocks",
            "barcode",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "description",
            "category",
            "previous_id",
            "next_id",
        ]
        read_only_fields = ["created_at", "updated_at"]


class StockMovementSerializer(ModelSerializer):
    class Meta:
        model = models.StockMovement
        fields = ["warehouse_item_stock", "amount", "related_movement"]


class StockUnitNestedSerializer(UniqueFieldsMixin, ModelSerializer):
    # id = serializers.IntegerField(required=False)

    class Meta:
        model = models.StockUnit
        fields = ["id", "name"]


class WarehouseItemStockINFO_ONLYSerializer(ModelSerializer):
    """this exists so that warehouseitemstock is available in ItemNestedSerializer has access
    to warehouseitemstock if it exists, so there won't be an unnecessary query to database
    to get the warehouseitemstock"""

    warehouse = serializers.IntegerField(write_only=True)
    id = serializers.IntegerField()

    class Meta:
        model = models.WarehouseItemStock
        fields = ["id", "warehouse"]
        # on purpose
        validators = []


class ItemNestedSerializer(UniqueFieldsMixin, ModelSerializer):
    stock_unit = StockUnitNestedSerializer()
    stocks = WarehouseItemStockINFO_ONLYSerializer(many=True)
    id = serializers.IntegerField(required=False)

    def create(self, validated_data: OrderedDict):
        stock_unit_data: OrderedDict = validated_data.pop("stock_unit")
        if stock_unit_data.get("id"):
            stock_unit = models.StockUnit.objects.get(id=stock_unit_data["id"])
        else:
            stock_unit = StockUnitSerializer().create(stock_unit_data)
        return super().create({**validated_data, "stock_unit_id": stock_unit.id})

    class Meta:
        model = models.Item
        fields = [
            "id",
            "name",
            "description",
            "stock_unit",
            "barcode",
            "stocks",
            "stock_code",
            "buyprice",
            "buycurrency",
            "sellprice",
            "sellcurrency",
        ]


class WarehouseItemStockNestedSerializer(ModelSerializer):
    """for creating Item if needed from stock WarehouseItemStock"""

    item = ItemNestedSerializer()
    amount = serializers.DecimalField(max_digits=19, decimal_places=4, read_only=True)

    # warehouse will be passed by InvoiceDetailSerializer downward,
    # setting this required=False so that client side won't have to pass
    # warehouse to every single invoiceItem
    warehouse = serializers.IntegerField(required=False, write_only=True)

    def create(self, validated_data: OrderedDict):
        item_data: OrderedDict = validated_data.pop("item")
        if item_data.get("id"):
            item = models.Item.objects.get(id=item_data["id"])
        else:
            item = ItemNestedSerializer().create(item_data)
        return super().create({**validated_data, "item_id": item.id})

    class Meta:
        model = models.WarehouseItemStock
        validators = []
        fields = ["item", "warehouse", "amount"]


class StockMovementNestedSerializer(ModelSerializer):
    """for creating WarehouseItemStock from StockMovement"""

    warehouse_item_stock = WarehouseItemStockNestedSerializer()
    amount = serializers.DecimalField(max_digits=19, decimal_places=4)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["amount"] = "{:f}".format(abs(instance.amount))
        return data

    @staticmethod
    def extract_warehouse_item_stock_id(warehouse_item_stock_data: OrderedDict):
        item_data = warehouse_item_stock_data["item"]
        warehouse = warehouse_item_stock_data["warehouse"]
        for stock in item_data["stocks"]:
            if stock["warehouse"] == warehouse.id:
                return stock["id"]

    def create(self, validated_data: OrderedDict):
        warehouse_item_stock_data: OrderedDict[
            str, OrderedDict | Any
        ] = validated_data.pop("warehouse_item_stock")
        try:
            warehouse_item_stock_id = self.extract_warehouse_item_stock_id(
                warehouse_item_stock_data
            )
            if not warehouse_item_stock_id:
                warehouse_item_stock_id = models.WarehouseItemStock.objects.get(
                    item=warehouse_item_stock_data["item"]["id"],
                    warehouse=warehouse_item_stock_data["warehouse"],
                ).id
        except models.WarehouseItemStock.DoesNotExist:
            warehouse_item_stock_id = WarehouseItemStockNestedSerializer().create(
                warehouse_item_stock_data
            ).id

        stock_movement = models.StockMovement(
            **validated_data, warehouse_item_stock_id=warehouse_item_stock_id
        )
        return stock_movement
        # return super().create(
        #     {**validated_data, "warehouse_item_stock": warehouse_item_stock}
        # )

    def update(self, instance: models.StockMovement, validated_data: OrderedDict):
        # we don't really want to update WarehouseItemStock like this. so just pop it.
        validated_data.pop("warehouse_item_stock")
        return super().update(instance, validated_data)

    class Meta:
        model = models.StockMovement
        fields = ["warehouse_item_stock", "amount", "related_movement"]


# TODO: Merge Items that may be duplicate with a view
