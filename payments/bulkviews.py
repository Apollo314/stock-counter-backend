from rest_framework import generics

from payments import models
from payments import serializers as payment_serializers
from utilities.bulkviewmixins import BulkDeleteMixin


class BulkBankViews(BulkDeleteMixin, generics.GenericAPIView):
    serializer_class = payment_serializers.BankSerializer
    queryset = models.Bank.objects.all()


class BulkPaymentAccountViews(BulkDeleteMixin, generics.GenericAPIView):
    serializer_class = payment_serializers.PaymentAccountOutSimpleSerializer
    queryset = models.PaymentAccount.objects.all()


class BulkPaymentViews(BulkDeleteMixin, generics.GenericAPIView):
    serializer_class = payment_serializers.PaymentOutSerializer
    queryset = models.Payment.objects.all()
