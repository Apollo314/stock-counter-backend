from datetime import date

from ninja import ModelSchema, Schema

from .models import Item


class ItemSchemaIn(ModelSchema):
    class Config:
        model = Item
        model_fields = [
            "id",
            "name",
            "stock_unit",
            "buyprice",
            "buycurrency",
            "sellprice",
            "sellcurrency",
            "kdv",
            "stock_code",
            "barcode",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "description",
            "category",
        ]


class ItemSchemaInLight(ModelSchema):
    class Config:
        model = Item
        model_fields = [
            "id",
            "name",
            "stock_unit",
            "buyprice",
            "buycurrency",
            "sellprice",
            "sellcurrency",
        ]
