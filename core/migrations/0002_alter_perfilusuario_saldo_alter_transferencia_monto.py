# Generated by Django 4.2.1 on 2023-06-14 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="perfilusuario",
            name="saldo",
            field=models.IntegerField(default=10000),
        ),
        migrations.AlterField(
            model_name="transferencia", name="monto", field=models.IntegerField(),
        ),
    ]