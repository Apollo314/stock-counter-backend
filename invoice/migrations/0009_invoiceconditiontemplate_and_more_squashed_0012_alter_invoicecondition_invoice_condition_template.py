# Generated by Django 4.2 on 2023-05-03 12:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    replaces = [
        ("invoice", "0009_invoiceconditiontemplate_and_more"),
        ("invoice", "0010_invoicecondition"),
        ("invoice", "0011_alter_invoicecondition_invoice"),
        ("invoice", "0012_alter_invoicecondition_invoice_condition_template"),
    ]

    dependencies = [
        ("invoice", "0008_alter_invoicecondition_condition_name_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="InvoiceConditionTemplate",
            fields=[
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="Created at"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, null=True, verbose_name="Updated at"
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("conditions", models.TextField(verbose_name="Invoice conditions")),
                (
                    "condition_name",
                    models.CharField(
                        max_length=100,
                        unique=True,
                        verbose_name="Condition identifier name (ex: Default conditions)",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_%(class)s",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created by",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="updated_%(class)s",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Updated by",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.RemoveField(
            model_name="invoice",
            name="invoice_conditions",
        ),
        migrations.DeleteModel(
            name="InvoiceCondition",
        ),
        migrations.CreateModel(
            name="InvoiceCondition",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("conditions", models.TextField(verbose_name="Invoice conditions")),
                (
                    "invoice",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invoice_condition",
                        to="invoice.invoice",
                        verbose_name="Invoice",
                    ),
                ),
                (
                    "invoice_condition_template",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="invoice_conditions",
                        to="invoice.invoiceconditiontemplate",
                        verbose_name="Invoice Condition Template",
                    ),
                ),
            ],
        ),
    ]
