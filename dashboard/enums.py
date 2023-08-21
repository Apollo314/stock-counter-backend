from dashboard.widgets import (
    Balance,
    BalanceGraph,
    BestCustomers,
    DuePayments,
    LastInvoices,
    LastItems,
    LeftoverItems,
)

from django.db import models


class WidgetsEnum(models.TextChoices):
    balance = Balance().unique_name
    balange_graph = BalanceGraph().unique_name
    best_customers = BestCustomers().unique_name
    due_payments = DuePayments().unique_name
    last_invoices = LastInvoices().unique_name
    last_items = LastItems().unique_name
    leftover_items = LeftoverItems().unique_name
