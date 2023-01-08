from rest_framework import generics
from rest_framework.parsers import JSONParser

from inventory import models
from inventory import serializers as inventory_serializers
from utilities.bulkviewmixins import BulkDeleteMixin, BulkPatchMixin


class BulkItemViews(BulkPatchMixin, BulkDeleteMixin, generics.GenericAPIView):
    parser_classes = [JSONParser]
    serializer_class = inventory_serializers.ItemInSerializer
    queryset = models.Item.objects.all()


class BulkCategoryViews(BulkDeleteMixin, generics.GenericAPIView):
    serializer_class = inventory_serializers.CategorySerializer
    queryset = models.Category.objects.all()


class BulkStockUnitViews(BulkDeleteMixin, generics.GenericAPIView):
    serializer_class = inventory_serializers.StockUnitSerializer
    queryset = models.StockUnit.objects.all()


class BulkWarehouseViews(BulkDeleteMixin, generics.GenericAPIView):
    serializer_class = inventory_serializers.WarehouseSerializer
    queryset = models.Warehouse.objects.all()
