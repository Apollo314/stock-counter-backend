from rest_framework import serializers

from stakeholder import models
from utilities.serializers import ModelSerializer


class StakeholderEmployeeSerializer(ModelSerializer):
    class Meta:
        model = models.StakeholderEmployee
        fields = ["stakeholder", "position", "name", "phone", "email"]


class StakeholderSerializer(ModelSerializer):
    employees = StakeholderEmployeeSerializer(many=True, read_only=True)

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
