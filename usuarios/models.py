from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=15)
    estado = models.BooleanField(default=True)
    id_rol = models.ForeignKey('Rol', on_delete=models.CASCADE)
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)

    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'telefono']

    def save(self, *args, **kwargs):
        if not self.pk and self.password:
            self.set_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
 

class GrupoSanguineo(models.Model):
    id_sangre = models.AutoField(primary_key=True)  # Coincide con SERIAL
    tipo_sangre = models.CharField(max_length=5)

    class Meta:
        managed = False  # Muy importante: Django no la toca
        db_table = 'grupo_sanguineo'  # Exactamente como está en PostgreSQL

    def __str__(self):
        return self.tipo_sangre


class Paciente(models.Model):
    id_paciente = models.AutoField(primary_key=True)
    id_usuario = models.OneToOneField('Usuario', on_delete=models.CASCADE)
    id_sangre = models.ForeignKey(GrupoSanguineo, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.id_usuario.nombre} {self.id_usuario.apellido}"
    

class Especialidad(models.Model):
    id_especialidad = models.AutoField(primary_key=True)  # Serial en PostgreSQL, AutoField en Django
    nombre_especialidad = models.CharField(max_length=100)
    descripcion = models.TextField()

    class Meta:
        db_table = 'especialidad'  # El nombre de la tabla en PostgreSQL debe coincidir con el nombre en la base de datos

    def __str__(self):
        return self.nombre_especialidad


class CentroMedico(models.Model):
    idcentromedico = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    direccion = models.TextField()
    id_usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)  # Relación con el modelo User
    def __str__(self):
        return self.idcentromedico
    
class Doctor(models.Model):
    id_doctor = models.AutoField(primary_key=True)
    id_usuario = models.OneToOneField('Usuario', on_delete=models.CASCADE)
    numero_licencia = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"Dr. {self.id_usuario.nombre} {self.id_usuario.apellido} - Licencia: {self.numero_licencia}"

    def esta_autorizado(self):
        return DoctorCentro.objects.filter(id_doctor=self, aceptado_por_centromedico=True).exists()

class DoctorCentro(models.Model):
    id_doctorcentro = models.AutoField(primary_key=True)
    id_doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    id_centromedico = models.ForeignKey('CentroMedico', on_delete=models.CASCADE)
    aceptado_por_centromedico = models.BooleanField(default=False)

    class Meta:
        unique_together = ('id_doctor', 'id_centromedico')

    def __str__(self):
        estado = "Aceptado" if self.aceptado_por_centromedico else "Pendiente"
        return f"{self.id_doctor.id_usuario.nombre} {self.id_doctor.id_usuario.apellido} - {self.id_centromedico.nombre} - {estado}"
    id_doctorcentro = models.AutoField(primary_key=True)
    id_doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    id_centromedico = models.ForeignKey('CentroMedico', on_delete=models.CASCADE)
    aceptado_por_centromedico = models.BooleanField(default=False)

    def __str__(self):
        return f"Doctor {self.id_doctor} - Centro Médico {self.id_centromedico} - Aceptado: {self.aceptado_por_centromedico}"


class EspecialidadDoctor(models.Model):
    id = models.AutoField(primary_key=True)
    id_especialidad = models.ForeignKey('Especialidad', on_delete=models.CASCADE)  # Relación con la tabla Especialidad
    id_doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)  # Relación con la tabla Doctor

    def __str__(self):
        return f"{self.id_doctor} - {self.id_especialidad}"

# Tabla de alergias registradas en el sistema
class Alergia(models.Model):
    TIPO_ALERGIA = [
        ('medicamento', 'Medicamento'),
        ('alimento', 'Alimento'),
        ('ambiental', 'Ambiental'),
        ('otro', 'Otro'),
    ]

    nombre = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_ALERGIA)

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

# Relación entre un paciente y una alergia específica
class PacienteAlergia(models.Model):
    GRAVEDAD_CHOICES = [
        ('leve', 'Leve'),
        ('moderada', 'Moderada'),
        ('severa', 'Severa'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='alergias')
    alergia = models.ForeignKey(Alergia, on_delete=models.CASCADE)
    gravedad = models.CharField(max_length=10, choices=GRAVEDAD_CHOICES)
    observacion = models.TextField(blank=True, null=True)
    aprobado = models.BooleanField(default=False)
    doctor_aprobador = models.ForeignKey(Doctor, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ('paciente', 'alergia')

    def __str__(self):
        return f"{self.paciente} - {self.alergia} ({self.gravedad})"

class Vacuna(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    max_dosis = models.PositiveIntegerField(default=1)


    def __str__(self):
        return self.nombre


class RegistroVacuna(models.Model):
    paciente = models.ForeignKey('Paciente', on_delete=models.CASCADE, related_name='vacunas')
    vacuna = models.ForeignKey(Vacuna, on_delete=models.CASCADE)
    fecha_aplicacion = models.DateField()
    dosis = models.PositiveIntegerField()  # 1, 2, 3, ...
    observacion = models.TextField(blank=True, null=True)
    aprobado = models.BooleanField(default=False)
    doctor_aprobador = models.ForeignKey('Doctor', null=True, blank=True, on_delete=models.SET_NULL)

    def clean(self):
        # Validar que no se repita la misma dosis
        if RegistroVacuna.objects.filter(
            paciente=self.paciente,
            vacuna=self.vacuna,
            dosis=self.dosis
        ).exists():
            raise ValidationError(f"La dosis {self.dosis} ya fue registrada para esta vacuna.")

        # Validar que no se exceda la dosis máxima
        if self.dosis > self.vacuna.max_dosis:
            raise ValidationError(f"Esta vacuna solo permite hasta {self.vacuna.max_dosis} dosis.")

        # Validar que la dosis anterior ya exista, excepto para la 1ra
        if self.dosis > 1:
            dosis_anterior = self.dosis - 1
            if not RegistroVacuna.objects.filter(
                paciente=self.paciente,
                vacuna=self.vacuna,
                dosis=dosis_anterior
            ).exists():
                raise ValidationError(f"No puedes registrar la dosis {self.dosis} sin tener la dosis {dosis_anterior} registrada.")

    def __str__(self):
        return f"{self.paciente} - {self.vacuna.nombre} - Dosis {self.dosis}"

    
from django.db import models

class EnfermedadPersistente(models.Model):
    TIPO_ENFERMEDAD = [
        ('endocrina', 'Endocrina'),
        ('cardiovascular', 'Cardiovascular'),
        ('respiratoria', 'Respiratoria'),
        ('neurologica', 'Neurológica'),
        ('psiquiatrica', 'Psiquiátrica'),
        ('gastrointestinal', 'Gastrointestinal'),
        ('reumatologica', 'Reumatológica'),
        ('renal', 'Renal'),
        ('hematologica', 'Hematológica'),
        ('infectologia', 'Infectologia'),
    ]

    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_ENFERMEDAD, default='endocrina')

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"



class PacienteEnfermedadPersistente(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='enfermedades_persistentes')
    enfermedad = models.ForeignKey(EnfermedadPersistente, on_delete=models.CASCADE)
    fecha_diagnostico = models.DateField(blank=True, null=True)
    observacion = models.TextField(blank=True, null=True)
    aprobado = models.BooleanField(default=False)
    doctor_aprobador = models.ForeignKey(Doctor, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ('paciente', 'enfermedad')

    def __str__(self):
        return f"{self.paciente} - {self.enfermedad}"
    
class PruebaImagen(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='imagenes_prueba/')

    def __str__(self):
        return self.nombre
    


class MedicamentoCronico(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class PacienteMedicamentoCronico(models.Model):
    id = models.AutoField(primary_key=True)
    id_paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    id_medicamento_cronico = models.ForeignKey(MedicamentoCronico, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    dosis = models.CharField(max_length=50, blank=True)
    frecuencia = models.CharField(max_length=50, blank=True)
    observaciones = models.TextField(blank=True)
    aprobado = models.BooleanField(default=False)
    doctor_aprobador = models.ForeignKey(Doctor, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.id_paciente} - {self.id_medicamento_cronico}"


class DocumentoEscaneado(models.Model):
    archivo = models.FileField(upload_to='pdfs/')
    nombre = models.CharField(max_length=100)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
import os
from django.db import models

def ruta_archivo_examen(instance, filename):
    tipo = instance.tipo.lower().replace(' ', '_')
    categoria = instance.categoria.lower().replace(' ', '_')
    return os.path.join(f"examenes_/{tipo}/{categoria}", filename)

class ExamenLaboratorio(models.Model):
    TIPO_CHOICES = [
        ('laboratorio', 'Laboratorio'),
        ('pruebas_funcionales', 'Pruebas Funcionales'),
        ('cardiologia', 'Cardiología'),
        ('neurologia', 'Neurología'),
        ('informes_medicos', 'Informes Médicos'),
        ('otros_documentos', 'Otros Documentos'),
    ]

    CATEGORIA_CHOICES = [
        ('hematologia', 'Hematología'),
        ('bioquimica', 'Bioquímica'),
        ('orina_y_heces', 'Orina y Heces'),
        ('inmunologia', 'Inmunología'),
        ('espirometria', 'Espirometría'),
        ('prueba_esfuerzo', 'Prueba de Esfuerzo'),
        ('electrocardiograma', 'Electrocardiograma'),
        ('ecocardiograma', 'Ecocardiograma'),
        ('holter', 'Holter'),
        ('encefalograma', 'Encefalograma'),
        ('potenciales_evocados', 'Potenciales Evocados'),
        ('interconsultas', 'Interconsultas'),
        ('resumenes_clinicos', 'Resúmenes Clínicos'),
        ('referencias', 'Referencias'),
        ('otros', 'Otros'),
        ('sin_categoria', 'Sin categoría'),
    ]

    paciente = models.ForeignKey('Paciente', on_delete=models.CASCADE, related_name='examenes_laboratorio')
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    categoria = models.CharField(max_length=50, choices=CATEGORIA_CHOICES)
    nombre_examen = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    fecha_realizacion = models.DateField()
    archivo = models.FileField(upload_to=ruta_archivo_examen)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_examen} - {self.paciente.username} ({self.fecha_realizacion})"


def ruta_archivo_imagenologia(instance, filename):
    tipo = instance.tipo.lower().replace(' ', '_')
    categoria = instance.categoria.lower().replace(' ', '_')
    return os.path.join(f"examenes_imagenologia/{tipo}/{categoria}", filename)

class ExamenLabImagenologia(models.Model):
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='examenes_imagenologia')
    tipo = models.CharField(max_length=50)
    categoria = models.CharField(max_length=50)
    nombre_examen = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    fecha_realizacion = models.DateField()
    archivo = models.FileField(upload_to=ruta_archivo_imagenologia)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_examen} - {self.paciente.username} ({self.fecha_realizacion})"

from django.db import models
from usuarios.models import Paciente, Doctor  # Asegúrate de tenerlos importados

class Medicamento(models.Model):
    nombre_comercial = models.CharField(max_length=100)
    principio_activo = models.CharField(max_length=100)
    presentacion = models.CharField(max_length=100)
    concentracion = models.CharField(max_length=100)
    via_administracion = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100, blank=True)  # Ej: "Antibiótico", "Analgésico", "Antiinflamatorio"

    def __str__(self):
        return f"{self.nombre_comercial} - {self.concentracion} ({self.via_administracion})"

class TratamientoActual(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    frecuencia = models.TextField(blank=True)
    finalizado = models.BooleanField(default=False)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} ({self.paciente})"


class SeguimientoTratamiento(models.Model):
    tratamiento = models.ForeignKey(TratamientoActual, on_delete=models.CASCADE, related_name='seguimientos')
    fecha = models.DateField(auto_now_add=True)
    comentario = models.TextField()
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE,null=True,blank=True)  # Usuario del sistema # Indica el rol con el que hizo el seguimiento
    archivo = models.FileField(upload_to='seguimientos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Seguimiento de {self.tratamiento.nombre} - {self.fecha}"
    
class DoctorPaciente(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aceptado', 'Aceptado'),
        ('rechazado', 'Rechazado'),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='solicitudes_enviadas')
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='solicitudes_recibidas')
    comentario = models.TextField(blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    creado_en = models.DateTimeField(auto_now_add=True)
    aprobado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('doctor', 'paciente')

    def __str__(self):
        return f"{self.doctor} -> {self.paciente} ({self.estado})"


