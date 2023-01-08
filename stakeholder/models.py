from django.db import models


class StakeholderRole(models.TextChoices):
    supplier = "Satıcı"
    customer = "Müşteri"
    customer_and_supplier = "Müşteri ve Satıcı"


class SupplierManager(models.Manager):
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


class CustomerManager(models.Manager):
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
    role = models.CharField("Rolü", choices=StakeholderRole.choices, max_length=30)
    name = models.CharField("Tam Adı", max_length=400)
    shortname = models.CharField("Kısa/Takma Adı", max_length=100)
    phone = models.CharField("Telefon", null=True, blank=True, max_length=20)
    email = models.EmailField("E-Posta", null=True, blank=True, max_length=100)
    vkntckn = models.CharField("VKN/TCKN", max_length=40, null=True, blank=True)
    address = models.CharField("Adres", max_length=1000, null=True, blank=True)

    employees: models.QuerySet["StakeholderEmployee"]

    objects: models.Manager = models.Manager()
    customer: models.Manager = CustomerManager()
    supplier: models.Manager = SupplierManager()


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
