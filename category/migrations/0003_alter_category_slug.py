# Generated by Django 5.1.6 on 2025-02-20 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("category", "0002_alter_category_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="slug",
            field=models.SlugField(max_length=100, unique=True),
        ),
    ]
