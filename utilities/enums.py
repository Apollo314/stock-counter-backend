from django.db import models
from django.utils.translation import gettext_lazy as _


class Currency(models.TextChoices):
    turkish_lira = "TRY", _("Turkish lira")
    dollar = "USD", _("US dollars")
    euro = "EUR", _("Euro")
    pound = "GBP", _("Pound sterling")


class InvoiceType(models.TextChoices):
    purchase = "purchase"
    sale = "sale"
    refund_purchase = "refund-purchase"
    refund_sale = "refund-sale"
