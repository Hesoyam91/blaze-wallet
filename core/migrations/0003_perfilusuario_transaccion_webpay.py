# Generated by Django 4.2.1 on 2023-06-19 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_perfilusuario_saldo_alter_transferencia_monto'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfilusuario',
            name='transaccion_webpay',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
