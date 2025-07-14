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
    SEXO_CHOICES = [
    ('M', 'Masculino'),
    ('F', 'Femenino'),
    ('O', 'Otro'),
]

    NACIONALIDAD_CHOICES = [
    ('V', 'Venezolano'),
    ('E', 'Extranjero'),
]

    sexo = models.CharField(
    max_length=1,
    choices=SEXO_CHOICES,
    default='O'  # o 'M' / 'F' según prefieras
)
    nacionalidad = models.CharField(
    max_length=1,
    choices=NACIONALIDAD_CHOICES,
    default='V'  # o 'E' si prefieres
    )



    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'telefono']

    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
 


class PerfilBebe(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(
        max_length=10,
        choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')],
        blank=True,
        null=True
    )
    responsable = models.ForeignKey(
        'Usuario',
        on_delete=models.CASCADE,
        related_name='bebes_responsables'
    )

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

import uuid

class Paciente(models.Model):
    id_paciente = models.AutoField(primary_key=True)
    id_usuario = models.OneToOneField(
        'Usuario',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    id_sangre = models.ForeignKey(
        GrupoSanguineo,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    perfil_bebe = models.OneToOneField(
        'PerfilBebe',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, null=True, blank=True)

    def clean(self):
        if not self.id_usuario and not self.perfil_bebe:
            raise ValidationError("Debe tener un usuario o un perfil de bebé asociado.")
        if self.id_usuario and self.perfil_bebe:
            raise ValidationError("No puede tener usuario y perfil de bebé al mismo tiempo.")

    def __str__(self):
        if self.id_usuario:
            return f"{self.id_usuario.nombre} {self.id_usuario.apellido}"
        elif self.perfil_bebe:
            return f"{self.perfil_bebe.nombre} {self.perfil_bebe.apellido}"
        else:
            return "Paciente sin datos"

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
    id_usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre  # Mejor mostrar el nombre que el ID


    
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
        # Aquí convierto los objetos relacionados a strings usando sus __str__
        return f"{self.id_doctor} - {self.id_centromedico} - {estado}"


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
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='examenes_subidos')  # NUEVO CAMPO
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    categoria = models.CharField(max_length=50, choices=CATEGORIA_CHOICES)
    nombre_examen = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    fecha_realizacion = models.DateField()
    archivo = models.URLField(max_length=500)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_examen} - {self.paciente.username} ({self.fecha_realizacion})"


def ruta_archivo_imagenologia(instance, filename):
    tipo = instance.tipo.lower().replace(' ', '_')
    categoria = instance.categoria.lower().replace(' ', '_')
    return os.path.join(f"examenes_imagenologia/{tipo}/{categoria}", filename)

class ExamenLabImagenologia(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='examenes_imagenologia')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='imagenologia_subidos')
    tipo = models.CharField(max_length=50)
    categoria = models.CharField(max_length=50)
    nombre_examen = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    fecha_realizacion = models.DateField()
    
    # CAMBIO AQUI
    archivo = models.URLField(max_length=500, null=True, blank=True)

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
    consulta = models.ForeignKey('Consulta', on_delete=models.SET_NULL, null=True, blank=True, related_name='tratamientos')
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
        return f"{self.medicamento.nombre_comercial} ({self.paciente})"


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


class SignosVitales(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='signos_vitales')
    consulta = models.ForeignKey('Consulta', on_delete=models.SET_NULL, null=True, blank=True, related_name='signos_vitales')
    fecha = models.DateTimeField(auto_now_add=True)

    peso = models.FloatField(help_text="Peso en kg", null=True, blank=True)
    altura = models.FloatField(help_text="Talla en metros", null=True, blank=True)

    presion_sistolica = models.IntegerField(null=True, blank=True)
    presion_diastolica = models.IntegerField(null=True, blank=True)

    frecuencia_cardiaca = models.IntegerField(help_text="lpm", null=True, blank=True)
    frecuencia_respiratoria = models.IntegerField(help_text="rpm", null=True, blank=True)
    temperatura = models.FloatField(help_text="°C", null=True, blank=True)
    spo2 = models.IntegerField(help_text="Saturación de oxígeno %", null=True, blank=True)
    glucosa = models.IntegerField(help_text="mg/dL", null=True, blank=True)

    observaciones = models.TextField(blank=True, help_text="Comentario opcional del médico")

    def imc(self):
        if self.peso and self.altura:
            return round(self.peso / (self.altura ** 2), 2)
        return None

    def __str__(self):
        return f"Signos vitales de {self.paciente} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"

from django.db import models

class Consulta(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='consultas')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='consultas')
    fecha = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    sintomas = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Consulta {self.id} - {self.paciente} con {self.doctor} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"

class DiagnosticoConsulta(models.Model):
    consulta = models.OneToOneField(Consulta, on_delete=models.CASCADE, related_name='diagnostico')
    descripcion = models.CharField(max_length=255)
    

    def __str__(self):
        return f"Diagnóstico en Consulta {self.consulta.id}: {self.descripcion}"

    
class ExamenFuncional(models.Model):
    consulta = models.OneToOneField(Consulta, on_delete=models.CASCADE, related_name='examen_funcional')

    general = models.TextField()
    piel = models.TextField()
    cabeza = models.TextField()
    oidos = models.TextField()
    nariz = models.TextField()
    boca = models.TextField()
    respiratorio = models.TextField()
    osteomuscular = models.TextField()
    cardiovascular = models.TextField()
    gastrointestinal = models.TextField()
    genitourinario = models.TextField()
    nervioso = models.TextField()

    def __str__(self):
        return f"Examen Funcional de Consulta {self.consulta.id}"

class ExamenFisico(models.Model):
    consulta = models.OneToOneField(Consulta, on_delete=models.CASCADE, related_name='examen_fisico')

    general = models.TextField(blank=True, null=True)
    piel = models.TextField(blank=True, null=True)
    uñas = models.TextField(blank=True, null=True)
    cabeza = models.TextField(blank=True, null=True)
    ojos = models.TextField(blank=True, null=True)
    nariz = models.TextField(blank=True, null=True)
    oidos = models.TextField(blank=True, null=True)
    boca_faringe = models.TextField(blank=True, null=True)
    cuello = models.TextField(blank=True, null=True)
    ganglios = models.TextField(blank=True, null=True)
    torax = models.TextField(blank=True, null=True)
    pulmones = models.TextField(blank=True, null=True)
    corazon = models.TextField(blank=True, null=True)
    abdomen = models.TextField(blank=True, null=True)
    genitales = models.TextField(blank=True, null=True)
    recto = models.TextField(blank=True, null=True)
    osteomuscular = models.TextField(blank=True, null=True)
    neurologico_psiquico = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Examen Físico de Consulta {self.consulta.id}"

class EnfermedadComun(models.Model):
    TIPO_ENFERMEDAD = [
        ('respiratoria', 'Respiratoria'),
        ('viral', 'Viral'),
        ('bacterial', 'Bacteriana'),
        ('digestiva', 'Digestiva'),
        ('dermatologica', 'Dermatológica'),
        ('otros', 'Otros'),
    ]

    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_ENFERMEDAD, default='otros')

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


class PacienteEnfermedadComun(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='enfermedades_comunes')
    enfermedad = models.ForeignKey(EnfermedadComun, on_delete=models.CASCADE)
    fecha_diagnostico = models.DateField(auto_now_add=True)
    fecha_recuperacion = models.DateField(null=True, blank=True)
    observacion = models.TextField(blank=True, null=True)
    aprobado = models.BooleanField(default=False)
    doctor_aprobador = models.ForeignKey(Doctor, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-fecha_diagnostico']

    def esta_activa(self):
        return self.fecha_recuperacion is None

    def __str__(self):
        return f"{self.paciente} - {self.enfermedad} ({self.fecha_diagnostico})"
