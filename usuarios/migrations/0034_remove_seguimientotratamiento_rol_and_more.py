# Generated by Django 5.1.7 on 2025-05-23 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0033_seguimientotratamiento_rol_alter_usuario_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='seguimientotratamiento',
            name='rol',
        ),
        migrations.AlterField(
            model_name='usuario',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
