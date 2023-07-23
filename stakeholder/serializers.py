from payments.models import Bank, PaymentAccount
from stakeholder import models
from utilities.serializers import ModelSerializer


class StakeholderEmployeeSerializer(ModelSerializer):
    class Meta:
        model = models.StakeholderEmployee
        fields = ["stakeholder", "position", "name", "phone", "email"]


class BankForStakeholderPaymentAccountSerializer(ModelSerializer):
    class Meta:
        model = Bank
        fields = ["name"]


class PaymentAccountForStakeholderSerializer(ModelSerializer):
    bank = BankForStakeholderPaymentAccountSerializer()

    class Meta:
        model = PaymentAccount
        fields = [
            "id",
            "created_at",
            "updated_at",
            "name",
            "bank",
            "account_number",
            "iban",
        ]


class StakeholderSerializer(ModelSerializer):
    employees = StakeholderEmployeeSerializer(many=True, read_only=True)
    paymentaccount_set = PaymentAccountForStakeholderSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = models.Stakeholder
        fields = [
            "id",
            "name",
            "role",
            "shortname",
            "phone",
            "email",
            "vkntckn",
            "address",
            "employees",
            "paymentaccount_set",
        ]


class StakeholderBasicSerializer(ModelSerializer):
    class Meta:
        model = models.Stakeholder
        fields = [
            "id",
            "name",
            "role",
            "shortname",
            "phone",
            "email",
            "vkntckn",
            "address",
        ]
