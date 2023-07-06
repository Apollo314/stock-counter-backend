from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.fields import OrderedDict

from payments.models import (Bank, CashPayment, ChequePayment,
                             InvoiceCashPayment, InvoiceChequePayment, Payment,
                             PaymentAccount)
from stakeholder.serializers import StakeholderSerializer
from users.serializers import UserSerializer
from utilities.serializer_helpers import (CurrentUserCreatedBy,
                                          CurrentUserDefault)
from utilities.serializers import ModelSerializer


class BankSerializer(ModelSerializer):
    created_by = serializers.HiddenField(default=CurrentUserCreatedBy())
    updated_by = serializers.HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Bank
        fields = ["id", "created_by", "updated_by", "created_at", "updated_at", "name"]


class BankOutSerializer(BankSerializer):
    created_by = UserSerializer()
    updated_by = UserSerializer()


class PaymentAccountOutSerializer(ModelSerializer):
    created_by = UserSerializer()
    updated_by = UserSerializer()
    bank = BankSerializer()
    stakeholder = StakeholderSerializer(required=False)

    class Meta:
        model = PaymentAccount
        fields = [
            "id",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "name",
            "bank",
            "account_number",
            "iban",
            "stakeholder",
        ]


class PaymentAccountInSerializer(ModelSerializer):
    created_by = serializers.HiddenField(
        default=CurrentUserCreatedBy(), label=_("Created by")
    )
    updated_by = serializers.HiddenField(
        default=CurrentUserDefault(), label=_("Updated by")
    )
    field_overrides = {
        "stakeholder": {"component": "stakeholder-selector"},
        "bank": {"component": "bank-selector"},
    }

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    class Meta:
        model = PaymentAccount
        fields = [
            "id",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "name",
            "bank",
            "account_number",
            "iban",
            "stakeholder",
        ]


class PaymentSerializer(ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "payer",
            "receiver",
            "amount",
            "currency",
        ]


class ChequePaymentSerializer(ModelSerializer):
    payment = PaymentSerializer(label=_("Payment info"))

    class Meta:
        model = ChequePayment
        fields = [
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "payment",
            "cheque_number",
        ]


class CashPaymentSerializer(ModelSerializer):
    payment = PaymentSerializer(label=_("Payment info"))

    def create(self, validated_data: OrderedDict):
        payment_data = validated_data.pop("payment")
        payment = PaymentSerializer().create(payment_data)
        validated_data["payment"] = payment
        return super().create(validated_data)

    def update(self, instance: CashPayment, validated_data: OrderedDict):
        payment_data = validated_data.pop("payment")
        PaymentSerializer().update(instance.payment, payment_data)
        super().update(validated_data)

    class Meta:
        model = CashPayment
        fields = [
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "payment",
        ]


class InvoiceChequePaymentSerializer(ModelSerializer):
    cheque_payment = ChequePaymentSerializer(label=_("Cheque Payment Info"))

    class Meta:
        model = InvoiceChequePayment
        fields = [
            "cheque_payment",
            "invoice",
        ]


class InvoiceCashPaymentSerializer(ModelSerializer):
    cash_payment = ChequePaymentSerializer(label=_("Cash Payment Info"))

    def create(self, validated_data):
        cash_payment_data = validated_data.pop("cash_payment")
        cash_payment = CashPaymentSerializer().create(cash_payment_data)
        validated_data["cash_payment"] = cash_payment
        return super().create(validated_data)

    def update(self, instance: InvoiceCashPayment, validated_data: OrderedDict):
        cash_payment_data = validated_data.pop("cash_payment")
        CashPaymentSerializer().update(instance.cash_payment, cash_payment_data)
        return super().update(validated_data)

    class Meta:
        model = InvoiceCashPayment
        fields = [
            "cash_payment",
            "invoice",
        ]
