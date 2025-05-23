# Generated by Django 5.1.7 on 2025-05-19 18:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0026_registrovacuna_delete_vacunapaciente'),
    ]

    operations = [
        migrations.CreateModel(
            name='TratamientoActual',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('descripcion', models.TextField(blank=True)),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField(blank=True, null=True)),
                ('finalizado', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('doctor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='usuarios.doctor')),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.paciente')),
            ],
        ),
        migrations.CreateModel(
            name='SeguimientoTratamiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(auto_now_add=True)),
                ('comentario', models.TextField()),
                ('autor', models.CharField(max_length=100)),
                ('archivo', models.FileField(blank=True, null=True, upload_to='seguimientos/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('tratamiento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seguimientos', to='usuarios.tratamientoactual')),
            ],
        ),
    ]
