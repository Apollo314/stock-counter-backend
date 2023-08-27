# Generated by Django 4.2 on 2023-08-27 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0008_payment_payment_done_alter_payment_currency"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentaccount",
            name="account_currency",
            field=models.CharField(
                choices=[
                    ("TRY", "Turkish lira"),
                    ("USD", "US dollars"),
                    ("EUR", "Euro"),
                    ("GBP", "Pound sterling"),
                ],
                default="TRY",
                max_length=4,
                verbose_name="Account currency",
            ),
        ),
    ]
