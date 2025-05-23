# Generated by Django 5.1.7 on 2025-05-11 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0015_enfermedadpersistente_tipo_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enfermedadpersistente',
            name='tipo',
            field=models.CharField(choices=[('endocrina', 'Endocrina'), ('cardiovascular', 'Cardiovascular'), ('respiratoria', 'Respiratoria'), ('neurologica', 'Neurológica'), ('psiquiatrica', 'Psiquiátrica'), ('gastrointestinal', 'Gastrointestinal'), ('reumatologica', 'Reumatológica'), ('renal', 'Renal'), ('hematologica', 'Hematológica'), ('infectologia', 'Infectologia')], default='endocrina', max_length=20),
        ),
        migrations.AlterUniqueTogether(
            name='doctorcentro',
            unique_together={('id_doctor', 'id_centromedico')},
        ),
    ]
