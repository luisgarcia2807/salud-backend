from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import authenticate
from .models import Alergia, EnfermedadPersistente, ExamenLabImagenologia, ExamenLaboratorio, GrupoSanguineo, MedicamentoCronico, PacienteAlergia, PacienteEnfermedadPersistente, PacienteMedicamentoCronico, Usuario, Paciente, Doctor, Especialidad, EspecialidadDoctor, CentroMedico, DoctorCentro, Vacuna
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
        fields = ['id_paciente', 'id_usuario', 'id_sangre']

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
from .models import RegistroVacuna  # o VacunaPaciente si dejaste el modelo anterior
class RegistroVacunaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroVacuna
        fields = '__all__'

    def validate(self, data):
        paciente = data.get('paciente')
        vacuna = data.get('vacuna')
        dosis = data.get('dosis')

        # Verificar si ya tiene esa misma dosis registrada
        if RegistroVacuna.objects.filter(paciente=paciente, vacuna=vacuna, dosis=dosis).exists():
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
