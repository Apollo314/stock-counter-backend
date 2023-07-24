from typing import TypeVar

from django.db import models
from django.utils.translation import gettext_lazy as _


class StakeholderRole(models.TextChoices):
    supplier = "Satıcı"
    customer = "Müşteri"
    customer_and_supplier = "Müşteri ve Satıcı"


T = TypeVar("T")


class SupplierManager(models.Manager[T]):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                role__in=[
                    StakeholderRole.supplier,
                    StakeholderRole.customer_and_supplier,
                ]
            )
        )


class CustomerManager(models.Manager[T]):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                role__in=[
                    StakeholderRole.customer,
                    StakeholderRole.customer_and_supplier,
                ]
            )
        )


class Stakeholder(models.Model):
    role = models.CharField(_("Role"), choices=StakeholderRole.choices, max_length=30)
    name = models.CharField(_("Full name"), max_length=400)
    shortname = models.CharField(_("Short name"), max_length=100)
    phone = models.CharField(_("Phone"), null=True, blank=True, max_length=20)
    email = models.EmailField(_("Email"), null=True, blank=True, max_length=100)
    vkntckn = models.CharField(_("VKN/TCKN"), max_length=40, null=True, blank=True)
    address = models.CharField(_("Address"), max_length=1000, null=True, blank=True)

    employees: models.QuerySet["StakeholderEmployee"]

    objects = models.Manager["Stakeholder"]()
    customer = CustomerManager["Stakeholder"]()
    supplier = SupplierManager["Stakeholder"]()


class StakeholderEmployee(models.Model):
    stakeholder: Stakeholder = models.ForeignKey(
        Stakeholder,
        verbose_name="temsil ettiği kurum ya da kişi",
        on_delete=models.CASCADE,
        related_name="employees",
    )
    position: str = models.CharField("Pozisyonu", max_length=100, null=True, blank=True)
    name = models.CharField("Adı", max_length=100)
    phone = models.CharField("Telefon", null=True, blank=True, max_length=20)
    email = models.CharField("E-Posta", null=True, blank=True, max_length=100)
