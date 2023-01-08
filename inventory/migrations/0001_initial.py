# Generated by Django 4.1.5 on 2023-01-08 22:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import inventory.models
import simple_history.models
import utilities.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=40, unique=True, verbose_name="Kategori"
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="inventory.category",
                        verbose_name="Üst Kategori",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Item",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="Oluşturma Tarihi",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, null=True, verbose_name="Değiştirme Tarihi"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=200, unique=True, verbose_name="Ürün/Hizmet"
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        blank=True, max_length=2000, null=True, verbose_name="Açıklama"
                    ),
                ),
                (
                    "buyprice",
                    models.DecimalField(
                        decimal_places=4, max_digits=19, verbose_name="Alış Fiyatı"
                    ),
                ),
                (
                    "buycurrency",
                    models.CharField(
                        choices=[
                            ("TRY", "Türk Lirası"),
                            ("USD", "US Dollars"),
                            ("EUR", "Euro"),
                            ("GBP", "Pound sterling"),
                        ],
                        default="TRY",
                        max_length=4,
                        verbose_name="Alış Para Birimi",
                    ),
                ),
                (
                    "sellprice",
                    models.DecimalField(
                        decimal_places=4, max_digits=19, verbose_name="Satış Fiyatı"
                    ),
                ),
                (
                    "sellcurrency",
                    models.CharField(
                        choices=[
                            ("TRY", "Türk Lirası"),
                            ("USD", "US Dollars"),
                            ("EUR", "Euro"),
                            ("GBP", "Pound sterling"),
                        ],
                        default="TRY",
                        max_length=4,
                        verbose_name="Satış Para Birimi",
                    ),
                ),
                (
                    "barcode",
                    models.CharField(
                        blank=True, max_length=20, null=True, verbose_name="Barkod"
                    ),
                ),
                (
                    "stock_code",
                    models.CharField(
                        blank=True, max_length=40, null=True, verbose_name="Stok Kodu"
                    ),
                ),
                (
                    "kdv",
                    models.IntegerField(
                        choices=[(0, "%0"), (1, "%1"), (8, "%8"), (18, "%18")],
                        verbose_name="Katma Değer Vergisi",
                    ),
                ),
                (
                    "thumbnail",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to=inventory.models.get_item_image_location,
                        verbose_name="Önizleme Fotoğraf",
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="inventory.category",
                        verbose_name="Kategori",
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
                        verbose_name="Oluşturan",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="StockUnit",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=20, unique=True, verbose_name="Birim"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Warehouse",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="Depo adı")),
                (
                    "address",
                    models.CharField(
                        blank=True,
                        max_length=200,
                        null=True,
                        verbose_name="Adress (varsa)",
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True, max_length=20, null=True, verbose_name="Telefon"
                    ),
                ),
                (
                    "mobile",
                    models.BooleanField(
                        default=False, verbose_name="Hareketli Depo(Araç)"
                    ),
                ),
                (
                    "plate_number",
                    models.CharField(
                        blank=True,
                        max_length=20,
                        null=True,
                        verbose_name="Plaka (varsa)",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="WarehouseItemStock",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=4,
                        default=0,
                        max_digits=19,
                        verbose_name="Stok Miktarı",
                    ),
                ),
                (
                    "item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stocks",
                        to="inventory.item",
                        verbose_name="Ürün",
                    ),
                ),
                (
                    "warehouse",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="stocks",
                        to="inventory.warehouse",
                        verbose_name="Depo",
                    ),
                ),
            ],
            options={
                "unique_together": {("item", "warehouse")},
            },
        ),
        migrations.CreateModel(
            name="StockMovement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="Oluşturma Tarihi",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, null=True, verbose_name="Değiştirme Tarihi"
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=4,
                        max_digits=19,
                        validators=[utilities.validators.not_zero_validator],
                        verbose_name="Miktar",
                    ),
                ),
                (
                    "movement_type",
                    models.CharField(
                        choices=[
                            ("purchase", "Purchase"),
                            ("sale", "Sale"),
                            ("refund-purchase", "Refund Purchase"),
                            ("refund-sale", "Refund Sale"),
                        ],
                        max_length=20,
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
                        verbose_name="Oluşturan",
                    ),
                ),
                (
                    "related_movement",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="inventory.stockmovement",
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
                        verbose_name="Değiştiren",
                    ),
                ),
                (
                    "warehouse_item_stock",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="inventory.warehouseitemstock",
                        verbose_name="Stok",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ItemImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        upload_to=inventory.models.get_item_image_location,
                        verbose_name="Ürün/Hizmet Fotoğrafı",
                    ),
                ),
                (
                    "description",
                    models.TextField(blank=True, null=True, verbose_name="Açıklama"),
                ),
                (
                    "item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="inventory.item",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="item",
            name="stock_unit",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="inventory.stockunit",
                verbose_name="Stok Birimi",
            ),
        ),
        migrations.AddField(
            model_name="item",
            name="updated_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="updated_%(class)s",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Değiştiren",
            ),
        ),
        migrations.CreateModel(
            name="HistoricalItem",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="Oluşturma Tarihi",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        blank=True,
                        editable=False,
                        null=True,
                        verbose_name="Değiştirme Tarihi",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_index=True, max_length=200, verbose_name="Ürün/Hizmet"
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        blank=True, max_length=2000, null=True, verbose_name="Açıklama"
                    ),
                ),
                (
                    "buyprice",
                    models.DecimalField(
                        decimal_places=4, max_digits=19, verbose_name="Alış Fiyatı"
                    ),
                ),
                (
                    "buycurrency",
                    models.CharField(
                        choices=[
                            ("TRY", "Türk Lirası"),
                            ("USD", "US Dollars"),
                            ("EUR", "Euro"),
                            ("GBP", "Pound sterling"),
                        ],
                        default="TRY",
                        max_length=4,
                        verbose_name="Alış Para Birimi",
                    ),
                ),
                (
                    "sellprice",
                    models.DecimalField(
                        decimal_places=4, max_digits=19, verbose_name="Satış Fiyatı"
                    ),
                ),
                (
                    "sellcurrency",
                    models.CharField(
                        choices=[
                            ("TRY", "Türk Lirası"),
                            ("USD", "US Dollars"),
                            ("EUR", "Euro"),
                            ("GBP", "Pound sterling"),
                        ],
                        default="TRY",
                        max_length=4,
                        verbose_name="Satış Para Birimi",
                    ),
                ),
                (
                    "barcode",
                    models.CharField(
                        blank=True, max_length=20, null=True, verbose_name="Barkod"
                    ),
                ),
                (
                    "stock_code",
                    models.CharField(
                        blank=True, max_length=40, null=True, verbose_name="Stok Kodu"
                    ),
                ),
                (
                    "kdv",
                    models.IntegerField(
                        choices=[(0, "%0"), (1, "%1"), (8, "%8"), (18, "%18")],
                        verbose_name="Katma Değer Vergisi",
                    ),
                ),
                (
                    "thumbnail",
                    models.TextField(
                        blank=True,
                        max_length=100,
                        null=True,
                        verbose_name="Önizleme Fotoğraf",
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="inventory.category",
                        verbose_name="Kategori",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Oluşturan",
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "stock_unit",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="inventory.stockunit",
                        verbose_name="Stok Birimi",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Değiştiren",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical item",
                "verbose_name_plural": "historical items",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
