from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.fields import OrderedDict

from payments.models import Bank, InvoicePayment, Payment, PaymentAccount
from stakeholder.serializers import StakeholderBasicSerializer, StakeholderSerializer
from users.serializers import UserSerializer
from utilities.serializer_helpers import CurrentUserCreatedBy, CurrentUserDefault
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


class PaymentAccountOutSimpleSerializer(ModelSerializer):
    stakeholder = StakeholderBasicSerializer(required=False)

    class Meta:
        model = PaymentAccount
        fields = [
            "name",
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
    created_by = serializers.HiddenField(
        default=CurrentUserCreatedBy(), label=_("Created by")
    )
    updated_by = serializers.HiddenField(
        default=CurrentUserDefault(), label=_("Updated by")
    )

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
            "additional_info",
            "due_date",
            "payment_type",
        ]


class PaymentOutSerializer(ModelSerializer):
    created_by = UserSerializer()
    updated_by = UserSerializer()
    payer = PaymentAccountOutSimpleSerializer()
    receiver = PaymentAccountOutSimpleSerializer()

    class Meta:
        model = Payment
        fields = [
            "id",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "payer",
            "receiver",
            "amount",
            "currency",
            "additional_info",
            "due_date",
            "payment_type",
        ]


class InvoicePaymentSerializer(ModelSerializer):
    payment = PaymentSerializer(label=_("Payment Info"))

    def create(self, validated_data):
        payment_data = validated_data.pop("payment")
        payment = PaymentSerializer().create(payment_data)
        validated_data["payment"] = payment
        return super().create(validated_data)

    def update(self, instance: InvoicePayment, validated_data: OrderedDict):
        payment_data = validated_data.pop("payment")
        PaymentSerializer().update(instance.payment, payment_data)
        return super().update(validated_data)

    class Meta:
        model = InvoicePayment
        fields = [
            "payment",
            "invoice",
        ]
