from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import authenticate
from .models import Alergia, EnfermedadPersistente, ExamenLabImagenologia, ExamenLaboratorio, GrupoSanguineo, MedicamentoCronico, PacienteAlergia, PacienteEnfermedadPersistente, PacienteMedicamentoCronico, PerfilBebe, Usuario, Paciente, Doctor, Especialidad, EspecialidadDoctor, CentroMedico, DoctorCentro, Vacuna
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    numero_licencia = serializers.CharField(write_only=True, required=False)
    id_especialidad = serializers.IntegerField(write_only=True, required=False)
    id_centromedico = serializers.IntegerField(write_only=True, required=False)
    id_sangre= serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Usuario
        fields = [
            'id_usuario', 'nombre', 'apellido', 'cedula', 'email', 'telefono',
            'fecha_nacimiento', 'estado', 'id_rol', 'password',
            'numero_licencia', 'id_especialidad', 'id_centromedico','id_sangre','foto_perfil',
        ]

    def validate(self, attrs):
        errores = {}

        if Usuario.objects.filter(email=attrs.get('email')).exists():
            errores['email'] = "Este correo ya está registrado."
        if Usuario.objects.filter(cedula=attrs.get('cedula')).exists():
            errores['cedula'] = "Esta cédula ya está registrada."
        if Usuario.objects.filter(telefono=attrs.get('telefono')).exists():
            errores['telefono'] = "Este número de teléfono ya está registrado."

        numero_licencia = attrs.get('numero_licencia')
        if numero_licencia and Doctor.objects.filter(numero_licencia=numero_licencia).exists():
            errores['numero_licencia'] = "Este número de licencia ya está registrado."

        if errores:
            raise serializers.ValidationError(errores)

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop('password')
        numero_licencia = validated_data.pop('numero_licencia', None)
        id_especialidad = validated_data.pop('id_especialidad', None)
        id_centromedico = validated_data.pop('id_centromedico', None)
        id_sangre=validated_data.pop('id_sangre', None)

        validated_data['username'] = validated_data.get('email')  # obligatorio para login

        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()

        # Crear paciente automáticamente
        Paciente.objects.create(id_usuario=usuario, id_sangre_id=id_sangre)  # O+

        # Si es doctor
        if numero_licencia:
            doctor = Doctor.objects.create(id_usuario=usuario, numero_licencia=numero_licencia)

            if id_especialidad:
                especialidad = Especialidad.objects.filter(id_especialidad=id_especialidad).first()
                if not especialidad:
                    raise serializers.ValidationError({"id_especialidad": "La especialidad no existe."})
                EspecialidadDoctor.objects.create(id_doctor=doctor, id_especialidad=especialidad)

            if id_centromedico:
                centro = CentroMedico.objects.filter(idcentromedico=id_centromedico).first()
                if not centro:
                    raise serializers.ValidationError({"id_centromedico": "El centro médico no existe."})
                DoctorCentro.objects.create(id_doctor=doctor, id_centromedico=centro, aceptado_por_centromedico=False)

        return usuario



class PerfilBebeRegistroSerializer(serializers.ModelSerializer):
    responsable_id = serializers.IntegerField(write_only=True)
    id_sangre = serializers.IntegerField(write_only=True)

    class Meta:
        model = PerfilBebe
        fields = [
            'id', 'nombre', 'apellido', 'fecha_nacimiento', 'sexo',
             'responsable_id', 'id_sangre'
        ]

    def validate_responsable_id(self, value):
        if not Usuario.objects.filter(id_usuario=value).exists():
            raise serializers.ValidationError("El usuario responsable no existe.")
        return value

    def validate_id_sangre(self, value):
        if not GrupoSanguineo.objects.filter(id_sangre=value).exists():
            raise serializers.ValidationError("El grupo sanguíneo no existe.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        responsable_id = validated_data.pop('responsable_id')
        id_sangre = validated_data.pop('id_sangre')

        responsable = Usuario.objects.get(id_usuario=responsable_id)
        perfil_bebe = PerfilBebe.objects.create(responsable=responsable, **validated_data)

        Paciente.objects.create(perfil_bebe=perfil_bebe, id_sangre_id=id_sangre)

        return perfil_bebe

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError("Debe proporcionar un email y una contraseña.")

        user = authenticate(username=email, password=password)
        if user is None:
            raise serializers.ValidationError("Credenciales inválidas.")

        data = super().validate(attrs)
        data.update({
            "id_usuario": user.id_usuario,
            "email": user.email,
            "nombre": user.nombre,
            "apellido": user.apellido,
        })
        return data


class CentroMedicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CentroMedico
        fields = ['idcentromedico', 'nombre']


class EspecialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidad
        fields = ['id_especialidad', 'nombre_especialidad']

class GrupoSanguineoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrupoSanguineo
        fields = ['id_sangre', 'tipo_sangre']  # Campos que quieres mostrar

class PacienteSerializer(serializers.ModelSerializer):
    # Serializador anidado para mostrar el nombre del grupo sanguíneo
    id_sangre = GrupoSanguineoSerializer(read_only=True)

    class Meta:
        model = Paciente
        fields = ['id_paciente', 'id_usuario','perfil_bebe', 'id_sangre']

# serializers.py


class AlergiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alergia
        fields = '__all__'

class PacienteAlergiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PacienteAlergia
        fields = '__all__'

# serializers.py


class VacunaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacuna
        fields = ['id', 'nombre', 'descripcion','max_dosis']


from rest_framework import serializers
from .models import RegistroVacuna

class RegistroVacunaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroVacuna
        fields = '__all__'

    def validate(self, data):
        # Tomamos los valores existentes si no se pasan en el PATCH
        paciente = data.get('paciente', getattr(self.instance, 'paciente', None))
        vacuna = data.get('vacuna', getattr(self.instance, 'vacuna', None))
        dosis = data.get('dosis', getattr(self.instance, 'dosis', None))

        # Si no se está modificando ninguno de estos campos, omite validación de dosis
        if self.instance and not any(campo in data for campo in ['paciente', 'vacuna', 'dosis']):
            return data

        # Verificar si ya tiene esa misma dosis registrada (excluyendo este mismo registro si es PATCH)
        if RegistroVacuna.objects.exclude(id=getattr(self.instance, 'id', None))\
            .filter(paciente=paciente, vacuna=vacuna, dosis=dosis).exists():
            raise serializers.ValidationError(f"El paciente ya tiene registrada la dosis {dosis} de esta vacuna.")

        # Validar que no se exceda la dosis máxima
        if vacuna and dosis > vacuna.max_dosis:
            raise serializers.ValidationError(f"La vacuna '{vacuna.nombre}' solo permite hasta {vacuna.max_dosis} dosis.")

        # Validar que la dosis anterior esté registrada si no es la primera
        if dosis > 1:
            dosis_anterior = dosis - 1
            if not RegistroVacuna.objects.filter(paciente=paciente, vacuna=vacuna, dosis=dosis_anterior).exists():
                raise serializers.ValidationError(f"No puedes registrar la dosis {dosis} sin haber registrado la dosis {dosis_anterior}.")

        return data



class EnfermedadPersistenteSerializer(serializers.ModelSerializer):
    class Meta:
        model= EnfermedadPersistente
        fields = '__all__'

class PacienteEnfermedadPersistenteSerializer(serializers.ModelSerializer):
    class Meta:
        model= PacienteEnfermedadPersistente
        fields = '__all__'

class UsuarioNombreApellidoCedulaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id_usuario','nombre', 'apellido', 'cedula']

class DoctorSerializer(serializers.ModelSerializer):
    # Usamos el nuevo serializador para Usuario con los campos deseados
    id_usuario = UsuarioNombreApellidoCedulaSerializer(read_only=True)

    # Comprobamos si el doctor está aceptado en algún centro médico
    activo = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = ['id_doctor', 'id_usuario', 'numero_licencia', 'activo']

    def get_activo(self, obj):
        # Verifica si el doctor ha sido aceptado por algún centro médico
        return DoctorCentro.objects.filter(id_doctor=obj, aceptado_por_centromedico=True).exists()

    
class DoctorCentroSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorCentro
        fields = ['id_doctor', 'id_centromedico', 'aceptado_por_centromedico']

    def update(self, instance, validated_data):
        # Cambiar el estado de aceptado_por_centromedico
        instance.aceptado_por_centromedico = validated_data.get('aceptado_por_centromedico', instance.aceptado_por_centromedico)
        instance.save()
        return instance
    
class MedicamentoCronicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicamentoCronico
        fields = ['id', 'nombre', 'descripcion']    


class PacienteMedicamentoCronicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PacienteMedicamentoCronico
        fields = ['id', 'id_paciente', 'id_medicamento_cronico', 'fecha_inicio', 'dosis', 'frecuencia', 'observaciones', 'aprobado', 'doctor_aprobador']

from rest_framework import serializers
from .models import DocumentoEscaneado

class DocumentoEscaneadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentoEscaneado
        fields = '__all__'



class ExamenLaboratorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamenLaboratorio
        fields = '__all__'
        read_only_fields = ['fecha_subida']

class ExamenImagenologiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamenLabImagenologia
        fields = '__all__'
        read_only_fields = ['fecha_subida']


from .models import TratamientoActual, SeguimientoTratamiento

class SeguimientoTratamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeguimientoTratamiento
        fields = '__all__'

class TratamientoActualSerializer(serializers.ModelSerializer):
    seguimientos = SeguimientoTratamientoSerializer(many=True, read_only=True)

    class Meta:
        model = TratamientoActual
        fields = '__all__'

    def validate(self, data):
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')

        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise serializers.ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio.")

        return data
from .models import Medicamento

class MedicamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicamento
        fields = '__all__'



class PacienteSerializercedula(serializers.ModelSerializer):
    nombre = serializers.CharField(source='id_usuario.nombre')
    apellido = serializers.CharField(source='id_usuario.apellido')
    cedula = serializers.CharField(source='id_usuario.cedula')

    class Meta:
        model = Paciente
        fields = ['id_paciente', 'nombre', 'apellido', 'cedula', 'id_sangre']


from .models import DoctorPaciente

class DoctorPacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorPaciente
        fields = '__all__'
        read_only_fields = ['estado', 'creado_en', 'aprobado_en']

from rest_framework import serializers
from .models import DoctorPaciente

class DoctorPacienteDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorPaciente
        fields = [
            'id',
            'comentario',
            'estado',
            'creado_en',
            'aprobado_en',
            'doctor',
            'paciente',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Datos del doctor
        doctor_usuario = getattr(instance.doctor, 'id_usuario', None)
        data['doctor_nombre'] = doctor_usuario.nombre if doctor_usuario else ''
        data['doctor_apellido'] = doctor_usuario.apellido if doctor_usuario else ''
        data['doctor_cedula'] = doctor_usuario.cedula if doctor_usuario else ''

        # Datos del paciente (usuario o perfil bebé)
        paciente = instance.paciente
        if paciente.id_usuario:
            data['paciente_nombre'] = paciente.id_usuario.nombre
            data['paciente_apellido'] = paciente.id_usuario.apellido
            data['paciente_cedula'] = paciente.id_usuario.cedula
        elif paciente.perfil_bebe:
            data['paciente_nombre'] = paciente.perfil_bebe.nombre
            data['paciente_apellido'] = paciente.perfil_bebe.apellido
            data['paciente_cedula'] = 'No tiene, es hijo'
        else:
            data['paciente_nombre'] = ''
            data['paciente_apellido'] = ''
            data['paciente_cedula'] = ''

        return data

from .models import SignosVitales

class SignosVitalesSerializer(serializers.ModelSerializer):
    imc = serializers.SerializerMethodField()
    paciente = serializers.PrimaryKeyRelatedField(queryset=Paciente.objects.all())

    class Meta:
        model = SignosVitales
        fields = [
            'id', 'paciente', 'fecha', 'peso', 'altura',
            'presion_sistolica', 'presion_diastolica',
            'frecuencia_cardiaca', 'frecuencia_respiratoria',
            'temperatura', 'spo2', 'glucosa', 'observaciones', 'imc'
        ]
        read_only_fields = ['id', 'fecha', 'imc']

    def get_imc(self, obj):
        return obj.imc()

    def validate(self, data):
        campos_vitales = [
            'peso', 'altura', 'presion_sistolica', 'presion_diastolica',
            'frecuencia_cardiaca', 'frecuencia_respiratoria',
            'temperatura', 'spo2', 'glucosa'
        ]
        if not any(data.get(campo) is not None for campo in campos_vitales):
            raise serializers.ValidationError("Debe registrar al menos un signo vital.")
        return data

from .models import Consulta
from rest_framework import serializers
from .serializers import SignosVitalesSerializer, TratamientoActualSerializer

class ConsultaSerializer(serializers.ModelSerializer):
    signos_vitales = SignosVitalesSerializer(many=True, read_only=True)
    tratamientos = TratamientoActualSerializer(many=True, read_only=True)

    class Meta:
        model = Consulta
        fields = ['id', 'paciente', 'doctor', 'fecha', 'motivo', 'observaciones', 'signos_vitales', 'tratamientos']
        read_only_fields = ['id', 'fecha']

from .models import DiagnosticoConsulta

class DiagnosticoConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosticoConsulta
        fields = ['id', 'consulta', 'descripcion', 'es_enfermedad_preexistente']

from rest_framework import serializers

class PacienteAlergiaHistoriaClinicaSerializer(serializers.ModelSerializer):
    nombre_alergia = serializers.CharField(source='alergia.nombre', read_only=True)
    tipo_alergia = serializers.CharField(source='alergia.get_tipo_display', read_only=True)

    class Meta:
        model = PacienteAlergia
        fields = ['nombre_alergia', 'tipo_alergia', 'gravedad', 'observacion']

class RegistroVacunaHistoriaClinicaSerializer(serializers.ModelSerializer):
    nombre_vacuna = serializers.CharField(source='vacuna.nombre', read_only=True)

    class Meta:
        model = RegistroVacuna
        fields = ['nombre_vacuna', 'dosis', 'fecha_aplicacion', 'observacion']

class EnfermedadPersistenteHistoriaClinicaSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source='enfermedad.nombre', read_only=True)
    tipo = serializers.CharField(source='enfermedad.get_tipo_display', read_only=True)

    class Meta:
        model = PacienteEnfermedadPersistente
        fields = ['nombre', 'tipo', 'fecha_diagnostico', 'observacion']

class MedicamentoCronicoHistoriaClinicaSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source='id_medicamento_cronico.nombre')
    descripcion = serializers.CharField(source='id_medicamento_cronico.descripcion')

    class Meta:
        model = PacienteMedicamentoCronico
        fields = ['nombre', 'descripcion', 'fecha_inicio', 'dosis', 'frecuencia', 'observaciones']

class ExamenLaboratorioHistoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamenLaboratorio
        fields = ['nombre_examen', 'tipo', 'categoria', 'descripcion', 'fecha_realizacion', 'archivo']

class ExamenImagenologiaHistoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamenLabImagenologia
        fields = ['nombre_examen', 'tipo', 'categoria', 'descripcion', 'fecha_realizacion', 'archivo']

class MedicamentoHCSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicamento
        fields = ['nombre_comercial', 'principio_activo', 'presentacion', 'concentracion', 'via_administracion', 'tipo']

class SeguimientoTratamientoHCSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeguimientoTratamiento
        fields = ['fecha', 'comentario', 'archivo']

class TratamientoActualHCSerializer(serializers.ModelSerializer):
    medicamento = MedicamentoHCSerializer(read_only=True)
    seguimientos = SeguimientoTratamientoHCSerializer(many=True, read_only=True)

    class Meta:
        model = TratamientoActual
        fields = [
            'medicamento', 'descripcion', 'fecha_inicio', 'fecha_fin',
            'frecuencia', 'finalizado', 'seguimientos'
        ]

class HistoriaClinicaPacienteSerializer(serializers.ModelSerializer):
    nombre = serializers.SerializerMethodField()
    apellido = serializers.SerializerMethodField()
    tipo_sangre = serializers.SerializerMethodField()

    consultas = ConsultaSerializer(many=True, read_only=True)
    signos_vitales = serializers.SerializerMethodField()
    tratamientos_actuales = serializers.SerializerMethodField()

    alergias = serializers.SerializerMethodField()
    vacunas = serializers.SerializerMethodField()
    enfermedades_persistentes = serializers.SerializerMethodField()
    medicamentos_cronicos = serializers.SerializerMethodField()
    examenes_laboratorio = serializers.SerializerMethodField()
    examenes_imagenologia = serializers.SerializerMethodField()


    class Meta:
        model = Paciente
        fields = [
            'id_paciente', 'nombre', 'apellido', 'tipo_sangre',
            'consultas', 'signos_vitales', 'tratamientos_actuales',
            'alergias', 'vacunas','enfermedades_persistentes', 'medicamentos_cronicos',
            'examenes_laboratorio', 'examenes_imagenologia'
        ]

    def get_nombre(self, obj):
        return obj.id_usuario.nombre if obj.id_usuario else obj.perfil_bebe.nombre

    def get_apellido(self, obj):
        return obj.id_usuario.apellido if obj.id_usuario else obj.perfil_bebe.apellido

    def get_tipo_sangre(self, obj):
        return obj.id_sangre.tipo_sangre if obj.id_sangre else None

    def get_signos_vitales(self, obj):
        ultimo_signo = obj.signos_vitales.order_by('-fecha').first()
        from .serializers import SignosVitalesSerializer
        return SignosVitalesSerializer(ultimo_signo).data if ultimo_signo else None

    def get_alergias(self, obj):
        from .serializers import PacienteAlergiaHistoriaClinicaSerializer
        alergias = obj.alergias.filter(aprobado=True)
        return PacienteAlergiaHistoriaClinicaSerializer(alergias, many=True).data

    def get_vacunas(self, obj):
        from .serializers import RegistroVacunaHistoriaClinicaSerializer
        vacunas = obj.vacunas.filter(aprobado=True).order_by('vacuna__nombre', 'dosis')
        return RegistroVacunaHistoriaClinicaSerializer(vacunas, many=True).data
    
    def get_enfermedades_persistentes(self, obj):
        from .serializers import EnfermedadPersistenteHistoriaClinicaSerializer
        enfermedades = obj.enfermedades_persistentes.filter(aprobado=True)
        return EnfermedadPersistenteHistoriaClinicaSerializer(enfermedades, many=True).data
    
    def get_medicamentos_cronicos(self, obj):
        from .serializers import MedicamentoCronicoHistoriaClinicaSerializer
        cronicos = obj.pacientemedicamentocronico_set.filter(aprobado=True)
        return MedicamentoCronicoHistoriaClinicaSerializer(cronicos, many=True).data
    
    def get_examenes_laboratorio(self, obj):
        from .serializers import ExamenLaboratorioHistoriaSerializer
        examenes = obj.examenes_laboratorio.all()
        return ExamenLaboratorioHistoriaSerializer(examenes, many=True).data

    def get_examenes_imagenologia(self, obj):
        from .serializers import ExamenImagenologiaHistoriaSerializer
        examenes = obj.examenes_imagenologia.all()
        return ExamenImagenologiaHistoriaSerializer(examenes, many=True).data
    
    def get_tratamientos_actuales(self, obj):
        tratamientos = TratamientoActual.objects.filter(paciente=obj)
        return TratamientoActualHCSerializer(tratamientos, many=True).data

