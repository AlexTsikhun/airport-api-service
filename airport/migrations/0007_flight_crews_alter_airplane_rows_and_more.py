# Generated by Django 4.2.13 on 2024-06-13 18:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("airport", "0006_alter_route_distance"),
    ]

    operations = [
        migrations.AddField(
            model_name="flight",
            name="crews",
            field=models.ManyToManyField(to="airport.crew"),
        ),
        migrations.AlterField(
            model_name="airplane",
            name="rows",
            field=models.SmallIntegerField(
                validators=[
                    django.core.validators.MaxValueValidator(40),
                    django.core.validators.MinValueValidator(1),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="airplane",
            name="seats_in_row",
            field=models.SmallIntegerField(
                validators=[
                    django.core.validators.MaxValueValidator(15),
                    django.core.validators.MinValueValidator(3),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="route",
            name="distance",
            field=models.PositiveSmallIntegerField(
                validators=[
                    django.core.validators.MaxValueValidator(17000),
                    django.core.validators.MinValueValidator(19),
                ]
            ),
        ),
    ]
