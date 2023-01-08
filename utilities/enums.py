from decimal import Decimal

from django.db import models


class Currency(models.TextChoices):
    turkish_lira = "TRY", "Türk Lirası"
    dollar = "USD", "US Dollars"
    euro = "EUR", "Euro"
    pound = "GBP", "Pound sterling"


class KDV(models.IntegerChoices):
    zero = 0, "%0"
    one = 1, "%1"
    eight = 8, "%8"
    eighteen = 18, "%18"


class InvoiceType(models.TextChoices):
    purchase = "purchase"
    sale = "sale"
    refund_purchase = "refund-purchase"
    refund_sale = "refund-sale"


class StockMovementType(models.TextChoices):
    purchase = "purchase"
    sale = "sale"
    refund_purchase = "refund-purchase"
    refund_sale = "refund-sale"
