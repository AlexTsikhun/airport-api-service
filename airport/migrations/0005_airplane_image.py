# Generated by Django 5.0.6 on 2024-06-09 14:22

import airport.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("airport", "0004_alter_order_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="airplane",
            name="image",
            field=models.ImageField(
                null=True, upload_to=airport.models.airplane_image_file_path
            ),
        ),
    ]