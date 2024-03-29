# Generated by Django 4.2 on 2023-07-06 03:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        (
            "payments",
            "0003_alter_bank_created_by_alter_cashpayment_created_by_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="bank",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, null=True, verbose_name="Created at"
            ),
        ),
        migrations.AlterField(
            model_name="cashpayment",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, null=True, verbose_name="Created at"
            ),
        ),
        migrations.AlterField(
            model_name="chequepayment",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, null=True, verbose_name="Created at"
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, null=True, verbose_name="Created at"
            ),
        ),
        migrations.AlterField(
            model_name="paymentaccount",
            name="bank",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="payments.bank",
                verbose_name="Bank",
            ),
        ),
        migrations.AlterField(
            model_name="paymentaccount",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, null=True, verbose_name="Created at"
            ),
        ),
    ]
