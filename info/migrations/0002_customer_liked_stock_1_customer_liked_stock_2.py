# Generated by Django 4.2.5 on 2023-10-01 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("info", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="liked_stock_1",
            field=models.CharField(default=" ", max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="customer",
            name="liked_stock_2",
            field=models.CharField(default=" ", max_length=10),
            preserve_default=False,
        ),
    ]
