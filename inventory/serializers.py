from typing import Any, OrderedDict

from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from inventory import models
from users.serializers import UserSerializer
from utilities.serializermixins import UniqueFieldsMixin
from utilities.serializers import (
    DynamicFieldsModelSerializer,
    ModelSerializer,
    UpdateListSerializer,
)
from drf_extra_fields.fields import Base64ImageField


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
    class Meta:
        model = models.WarehouseItemStock
        fields = ["id", "item", "warehouse", "amount"]


class CurrentUserDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context["request"].user

    def __repr__(self):
        return "%s()" % self.__class__.__name__


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
    created_by = UserSerializer()
    updated_by = UserSerializer()


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


class ItemNestedSerializer(UniqueFieldsMixin, ModelSerializer):
    stock_unit = StockUnitNestedSerializer()
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

    # will be passed by InvoiceDetailSerializer downward,
    # setting this required=False so that client side won't have to pass
    # movement_type to every single invoiceItem
    movement_type = serializers.CharField(required=False)

    def create(self, validated_data: OrderedDict):
        warehouse_item_stock_data: OrderedDict[
            str, OrderedDict | Any
        ] = validated_data.pop("warehouse_item_stock")
        try:
            warehouse_item_stock = models.WarehouseItemStock.objects.get(
                item=warehouse_item_stock_data["item"]["id"],
                warehouse=warehouse_item_stock_data["warehouse"],
            )
        except models.WarehouseItemStock.DoesNotExist:
            #     warehouse_item_stock = models.WarehouseItemStock.objects.create(
            #         item=warehouse_item_stock_data["item"]["id"],
            #         warehouse=warehouse_item_stock_data["warehouse"],
            #     )
            # else:
            warehouse_item_stock = WarehouseItemStockNestedSerializer().create(
                warehouse_item_stock_data
            )
        return super().create(
            {**validated_data, "warehouse_item_stock": warehouse_item_stock}
        )

    def update(self, instance: models.StockMovement, validated_data: OrderedDict):
        # we don't really want to update WarehouseItemStock like this. so just pop it.
        validated_data.pop("warehouse_item_stock")
        return super().update(instance, validated_data)

    class Meta:
        model = models.StockMovement
        fields = ["warehouse_item_stock", "amount", "related_movement", "movement_type"]


# TODO: Merge Items that may be duplicate with a view
