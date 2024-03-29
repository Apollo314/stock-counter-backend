# Generated by Django 4.1.5 on 2023-04-21 04:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("invoice", "0002_alter_invoiceitem_stock_movement"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invoice",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="Created at"
            ),
        ),
        migrations.AlterField(
            model_name="invoice",
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
            model_name="invoice",
            name="updated_at",
            field=models.DateTimeField(
                auto_now=True, null=True, verbose_name="Updated at"
            ),
        ),
        migrations.AlterField(
            model_name="invoice",
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
    ]
