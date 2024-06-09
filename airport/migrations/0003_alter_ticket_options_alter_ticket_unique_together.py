# Generated by Django 5.0.6 on 2024-06-08 09:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("airport", "0002_order_user"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="ticket",
            options={"ordering": ("row", "seat")},
        ),
        migrations.AlterUniqueTogether(
            name="ticket",
            unique_together={("row", "seat", "flight")},
        ),
    ]