# Generated by Django 5.1.6 on 2025-02-25 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order", name="tax", field=models.FloatField(default=0),
        ),
    ]
