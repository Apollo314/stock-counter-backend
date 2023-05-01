from rest_framework import generics

from invoice import models
from invoice import serializers as invoice_serializers
from utilities.bulkviewmixins import BulkDeleteMixin


class BulkInvoiceViews(BulkDeleteMixin, generics.GenericAPIView):
    serializer_class = invoice_serializers.InvoiceListSerializer
    queryset = models.Invoice.objects.all()

class BulkInvoiceConditionsViews(BulkDeleteMixin, generics.GenericAPIView):
    serializer_class = invoice_serializers.InvoiceConditionSerializerIn
    queryset = models.InvoiceCondition.objects.all()
