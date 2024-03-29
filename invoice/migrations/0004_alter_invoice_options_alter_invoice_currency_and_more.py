# Generated by Django 4.1.5 on 2023-04-30 10:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import invoice.models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0014_remove_warehouse_mobile_alter_category_name_and_more"),
        ("stakeholder", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("invoice", "0003_alter_invoice_created_at_alter_invoice_created_by_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="invoice",
            options={"permissions": [("view_all_invoices", "Can view all invoices")]},
        ),
        migrations.AlterField(
            model_name="invoice",
            name="currency",
            field=models.CharField(
                choices=[
                    ("TRY", "Türk Lirası"),
                    ("USD", "US Dollars"),
                    ("EUR", "Euro"),
                    ("GBP", "Pound sterling"),
                ],
                default="TRY",
                max_length=4,
                verbose_name="Invoice currency",
            ),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="currency_exchange_rate",
            field=models.DecimalField(
                blank=True,
                decimal_places=4,
                max_digits=19,
                null=True,
                verbose_name="Currency exchange rate",
            ),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="description",
            field=models.TextField(blank=True, null=True, verbose_name="Description"),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="invoice_type",
            field=models.CharField(
                choices=[
                    ("purchase", "Purchase"),
                    ("sale", "Sale"),
                    ("refund-purchase", "Refund Purchase"),
                    ("refund-sale", "Refund Sale"),
                ],
                max_length=20,
                verbose_name="Invoice type",
            ),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="last_payment_date",
            field=models.DateTimeField(
                default=invoice.models.week_from_now, verbose_name="Last payment date"
            ),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="name",
            field=models.CharField(max_length=100, verbose_name="Invoice name"),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="related_invoice",
            field=models.ManyToManyField(
                blank=True,
                related_name="refund_invoice",
                to="invoice.invoice",
                verbose_name="Related invoices",
            ),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="stakeholder",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="stakeholder.stakeholder",
                verbose_name="Stakeholder",
            ),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="total",
            field=models.DecimalField(
                blank=True,
                decimal_places=4,
                max_digits=19,
                null=True,
                verbose_name="Total without tax",
            ),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="total_with_tax",
            field=models.DecimalField(
                blank=True,
                decimal_places=4,
                max_digits=19,
                null=True,
                verbose_name="Total with tax",
            ),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="warehouse",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="invoices",
                to="inventory.warehouse",
                verbose_name="Depot",
            ),
        ),
        migrations.AlterField(
            model_name="invoiceitem",
            name="invoice",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="items",
                to="invoice.invoice",
                verbose_name="Related Invoice",
            ),
        ),
        migrations.AlterField(
            model_name="invoiceitem",
            name="price",
            field=models.DecimalField(
                decimal_places=4, max_digits=19, verbose_name="Price"
            ),
        ),
        migrations.AlterField(
            model_name="invoiceitem",
            name="stock_movement",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="invoice_item",
                to="inventory.stockmovement",
                verbose_name="Stock movement",
            ),
        ),
        migrations.CreateModel(
            name="InvoiceCondition",
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
                ("id", models.UUIDField(primary_key=True, serialize=False)),
                ("conditions", models.TextField(verbose_name="Invoice conditions")),
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
        migrations.AlterField(
            model_name="invoice",
            name="invoice_conditions",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="invoices",
                to="invoice.invoicecondition",
                verbose_name="Invoice Conditions",
            ),
        ),
    ]
