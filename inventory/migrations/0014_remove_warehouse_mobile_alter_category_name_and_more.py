# Generated by Django 4.1.5 on 2023-04-21 04:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import inventory.models
import utilities.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("inventory", "0013_tax_alter_historicalitem_barcode_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="warehouse",
            name="mobile",
        ),
        migrations.AlterField(
            model_name="category",
            name="name",
            field=models.CharField(max_length=40, unique=True, verbose_name="Category"),
        ),
        migrations.AlterField(
            model_name="historicalitem",
            name="barcode",
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=20,
                null=True,
                verbose_name="Barcode",
            ),
        ),
        migrations.AlterField(
            model_name="historicalitem",
            name="buycurrency",
            field=models.CharField(
                choices=[
                    ("TRY", "Türk Lirası"),
                    ("USD", "US Dollars"),
                    ("EUR", "Euro"),
                    ("GBP", "Pound sterling"),
                ],
                default="TRY",
                max_length=4,
                verbose_name="Buy currency",
            ),
        ),
        migrations.AlterField(
            model_name="historicalitem",
            name="buyprice",
            field=models.DecimalField(
                decimal_places=4, max_digits=19, verbose_name="Buy price"
            ),
        ),
        migrations.AlterField(
            model_name="historicalitem",
            name="category",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="inventory.category",
                verbose_name="Category",
            ),
        ),
        migrations.AlterField(
            model_name="historicalitem",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="Created at"
            ),
        ),
        migrations.AlterField(
            model_name="historicalitem",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Created by",
            ),
        ),
        migrations.AlterField(
            model_name="historicalitem",
            name="description",
            field=models.CharField(
                blank=True, max_length=2000, null=True, verbose_name="Description"
            ),
        ),
        migrations.AlterField(
            model_name="historicalitem",
            name="name",
            field=models.CharField(
                db_index=True, max_length=200, verbose_name="Item/Service"
            ),
        ),
        migrations.AlterField(
            model_name="historicalitem",
            name="sellcurrency",
            field=models.CharField(
                choices=[
                    ("TRY", "Türk Lirası"),
                    ("USD", "US Dollars"),
                    ("EUR", "Euro"),
                    ("GBP", "Pound sterling"),
                ],
                default="TRY",
                max_length=4,
                verbose_name="Sell currency",
            ),
        ),
        migrations.AlterField(
            model_name="historicalitem",
            name="sellprice",
            field=models.DecimalField(
                decimal_places=4, max_digits=19, verbose_name="Sell price"
            ),
        ),
        migrations.AlterField(
            model_name="historicalitem",
            name="stock_code",
            field=models.CharField(
                blank=True, max_length=40, null=True, verbose_name="Stock code"
            ),
        ),
        migrations.AlterField(
            model_name="historicalitem",
            name="stock_unit",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="inventory.stockunit",
                verbose_name="Stock unit",
            ),
        ),
        migrations.AlterField(
            model_name="historicalitem",
            name="thumbnail",
            field=models.TextField(
                blank=True, max_length=100, null=True, verbose_name="Thumbnail"
            ),
        ),
        migrations.AlterField(
            model_name="historicalitem",
            name="updated_at",
            field=models.DateTimeField(
                blank=True, editable=False, null=True, verbose_name="Updated at"
            ),
        ),
        migrations.AlterField(
            model_name="historicalitem",
            name="updated_by",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Updated by",
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="barcode",
            field=models.CharField(
                blank=True,
                max_length=20,
                null=True,
                unique=True,
                verbose_name="Barcode",
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="buycurrency",
            field=models.CharField(
                choices=[
                    ("TRY", "Türk Lirası"),
                    ("USD", "US Dollars"),
                    ("EUR", "Euro"),
                    ("GBP", "Pound sterling"),
                ],
                default="TRY",
                max_length=4,
                verbose_name="Buy currency",
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="buyprice",
            field=models.DecimalField(
                decimal_places=4, max_digits=19, verbose_name="Buy price"
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="inventory.category",
                verbose_name="Category",
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="Created at"
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="created_%(class)s",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Created by",
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="description",
            field=models.CharField(
                blank=True, max_length=2000, null=True, verbose_name="Description"
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="name",
            field=models.CharField(
                max_length=200, unique=True, verbose_name="Item/Service"
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="sellcurrency",
            field=models.CharField(
                choices=[
                    ("TRY", "Türk Lirası"),
                    ("USD", "US Dollars"),
                    ("EUR", "Euro"),
                    ("GBP", "Pound sterling"),
                ],
                default="TRY",
                max_length=4,
                verbose_name="Sell currency",
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="sellprice",
            field=models.DecimalField(
                decimal_places=4, max_digits=19, verbose_name="Sell price"
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="stock_code",
            field=models.CharField(
                blank=True, max_length=40, null=True, verbose_name="Stock code"
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="stock_unit",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="inventory.stockunit",
                verbose_name="Stock unit",
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="thumbnail",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=inventory.models.get_item_image_location,
                verbose_name="Thumbnail",
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="updated_at",
            field=models.DateTimeField(
                auto_now=True, null=True, verbose_name="Updated at"
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="updated_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="updated_%(class)s",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Updated by",
            ),
        ),
        migrations.AlterField(
            model_name="itemimage",
            name="image",
            field=models.ImageField(
                upload_to=inventory.models.get_item_image_location,
                verbose_name="Item/Service image",
            ),
        ),
        migrations.AlterField(
            model_name="stockmovement",
            name="amount",
            field=models.DecimalField(
                decimal_places=4,
                max_digits=19,
                validators=[utilities.validators.not_zero_validator],
                verbose_name="Amount",
            ),
        ),
        migrations.AlterField(
            model_name="stockmovement",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="Created at"
            ),
        ),
        migrations.AlterField(
            model_name="stockmovement",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="created_%(class)s",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Created by",
            ),
        ),
        migrations.AlterField(
            model_name="stockmovement",
            name="updated_at",
            field=models.DateTimeField(
                auto_now=True, null=True, verbose_name="Updated at"
            ),
        ),
        migrations.AlterField(
            model_name="stockmovement",
            name="updated_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="updated_%(class)s",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Updated by",
            ),
        ),
        migrations.AlterField(
            model_name="stockunit",
            name="name",
            field=models.CharField(
                max_length=20, unique=True, verbose_name="Stock unit"
            ),
        ),
        migrations.AlterField(
            model_name="warehouse",
            name="address",
            field=models.CharField(
                blank=True, max_length=200, null=True, verbose_name="Address"
            ),
        ),
        migrations.AlterField(
            model_name="warehouse",
            name="name",
            field=models.CharField(max_length=100, verbose_name="Depot name"),
        ),
        migrations.AlterField(
            model_name="warehouse",
            name="phone",
            field=models.CharField(
                blank=True, max_length=20, null=True, verbose_name="Phone"
            ),
        ),
        migrations.AlterField(
            model_name="warehouse",
            name="plate_number",
            field=models.CharField(
                blank=True, max_length=20, null=True, verbose_name="Plate number"
            ),
        ),
        migrations.AlterField(
            model_name="warehouseitemstock",
            name="amount_db",
            field=models.DecimalField(
                blank=True,
                decimal_places=4,
                default=None,
                max_digits=19,
                null=True,
                verbose_name="Amount",
            ),
        ),
        migrations.AlterField(
            model_name="warehouseitemstock",
            name="item",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="stocks",
                to="inventory.item",
                verbose_name="Item/Service",
            ),
        ),
        migrations.AlterField(
            model_name="warehouseitemstock",
            name="warehouse",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="stocks",
                to="inventory.warehouse",
                verbose_name="Depot name",
            ),
        ),
    ]
