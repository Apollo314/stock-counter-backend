# Generated by Django 4.2 on 2023-06-21 16:30

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="payment",
            old_name="buycurrency",
            new_name="currency",
        ),
    ]
