from django.db import models


class WidgetsEnum(models.TextChoices):
    balance = "balance"
    balange_graph = "balance_graph"
    best_customers = "best_customers"
    due_payments = "due_payments"
    last_invoices = "last_invoices"
    last_items = "last_items"
    leftover_items = "leftover_items"
    last_users = "last_users"
