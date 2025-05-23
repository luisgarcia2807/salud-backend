from rest_framework import viewsets, serializers, status
from .models import Alergia, Doctor, DoctorCentro, EnfermedadPersistente, ExamenLabImagenologia, ExamenLaboratorio, GrupoSanguineo, MedicamentoCronico, Paciente, PacienteAlergia, PacienteEnfermedadPersistente, PacienteMedicamentoCronico, RegistroVacuna, Usuario, Vacuna
from .serializers import AlergiaSerializer, DoctorSerializer, DocumentoEscaneadoSerializer, EnfermedadPersistenteSerializer, ExamenImagenologiaSerializer, ExamenLaboratorioSerializer, GrupoSanguineoSerializer, MedicamentoCronicoSerializer, PacienteAlergiaSerializer, PacienteEnfermedadPersistenteSerializer, PacienteMedicamentoCronicoSerializer, PacienteSerializer, RegistroVacunaSerializer, UsuarioSerializer, VacunaSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CentroMedico
from .serializers import CentroMedicoSerializer
from .models import Especialidad
from .serializers import EspecialidadSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .models import PruebaImagen
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import DocumentoEscaneado
from .serializers import DocumentoEscaneadoSerializer



class UsuarioDetailView(APIView):
    def get(self, request, id_usuario, *args, **kwargs):
        try:
            # Buscar usuario usando 'id_usuario'
            usuario = Usuario.objects.get(id_usuario=id_usuario)
            serializer = UsuarioSerializer(usuario)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Usuario.DoesNotExist:
            return Response({"detail": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        
# ViewSet para el manejo de usuarios
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()  # Obtiene todos los usuarios
    serializer_class = UsuarioSerializer  # Usa el serializador de usuarios
    permission_classes = [AllowAny]  # Permite que cualquiera acceda a este ViewSet (solo para pruebas)
    
    def create(self, request, *args, **kwargs):
        password = request.data.get('password')  # Obtener la contraseña en texto plano
        

        # Si necesitas lógica adicional antes de crear, como encriptar la contraseña
        return super().create(request, *args, **kwargs)

# Vista personalizada para obtener el token JWT
class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]  # Permitir que cualquier usuario acceda para pruebas

    def post(self, request, *args, **kwargs):
        # Obtiene el email y la contraseña del request
        email = request.data.get('email')
        password = request.data.get('password')

        # Verifica si se proporcionaron el email y la contraseña
        if not email or not password:
            return Response({"detail": "Debe proporcionar un email y una contraseña."},
                             status=status.HTTP_400_BAD_REQUEST)

        # Autenticar al usuario usando el email (en vez del username)
        user = authenticate(username=email, password=password)

        # Si las credenciales no son válidas
        if user is None:
            # Verificamos si el email existe
            try:
                user = Usuario.objects.get(email=email)
            except Usuario.DoesNotExist:
                # Si el usuario no existe, el error es por el email
                return Response({"detail": "El email no está registrado."},
                                 status=status.HTTP_404_NOT_FOUND)

            # Si el email existe pero la contraseña es incorrecta
            return Response({"detail": "Contraseña incorrecta. Intenta de nuevo."},
                             status=status.HTTP_401_UNAUTHORIZED)

        # Si las credenciales son correctas, generar el token
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Devolver el token y la información adicional del usuario
        return Response({
            'access': access_token,
            'refresh': str(refresh),
            'id_usuario': user.id_usuario,
            'email': user.email,
            'nombre': user.nombre,
            'apellido': user.apellido
        }, status=status.HTTP_200_OK)

# Vista para refrescar el token JWT
class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]  # Permitir que cualquier usuario acceda para pruebas

class CentroMedicoListView(APIView):
    def get(self, request):
        centros_medicos = CentroMedico.objects.all()  # Obtenemos todos los centros médicos
        serializer = CentroMedicoSerializer(centros_medicos, many=True)
        return Response(serializer.data)
    

class EspecialidadListView(APIView):
    def get(self, request):
        especialidades = Especialidad.objects.all()  # Obtenemos todas las especialidades
        serializer = EspecialidadSerializer(especialidades, many=True)
        return Response(serializer.data)

class GrupoSanguineoListView(APIView):
    def get(self, request):
        
        grupos_sanguineos = GrupoSanguineo.objects.all()
        serializer = GrupoSanguineoSerializer(grupos_sanguineos, many=True)
        return Response(serializer.data)


class PacientePorUsuarioView(APIView):
    def get(self, request, id_usuario):
        try:
            paciente = Paciente.objects.select_related('id_usuario', 'id_sangre').get(id_usuario=id_usuario)
            serializer = PacienteSerializer(paciente)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Paciente.DoesNotExist:
            return Response({"detail": "No se encontró paciente asociado a ese usuario."}, status=status.HTTP_404_NOT_FOUND)
        


class ListaAlergias(APIView):
    def get(self, request):
        tipo = request.GET.get('tipo', None)  # Obtiene el parámetro 'tipo' de la URL

        if tipo:
            # Filtra las alergias por el tipo especificado
            alergias = Alergia.objects.filter(tipo=tipo)
        else:
            # Si no se proporciona el parámetro 'tipo', retorna todas las alergias
            alergias = Alergia.objects.all()

        serializer = AlergiaSerializer(alergias, many=True)
        return Response(serializer.data)
    
class PacienteAlergiaViewSet(viewsets.ModelViewSet):
    queryset = PacienteAlergia.objects.all()
    serializer_class = PacienteAlergiaSerializer

class AlergiasPorPacienteView(APIView):
    def get(self, request, id_paciente):
        alergias = PacienteAlergia.objects.filter(paciente_id=id_paciente).select_related('alergia','doctor_aprobador__id_usuario')
        
        resultados = []
        for a in alergias:
            resultados.append({
                'id': a.id, 
                'nombre_alergia': a.alergia.nombre,
                'tipo_alergia': a.alergia.get_tipo_display(),
                'gravedad': a.get_gravedad_display(),
                'observacion': a.observacion,
                'aprobado': a.aprobado,
                'doctor_aprobador': (
                    f"{a.doctor_aprobador.id_usuario.nombre} {a.doctor_aprobador.id_usuario.apellido}"
                    if a.doctor_aprobador else None
                )

            })

        return Response(resultados, status=status.HTTP_200_OK)
    
class VacunaListView(APIView):
    def get(self, request):
        vacunas = Vacuna.objects.all()  # Obtener todas las vacunas
        serializer = VacunaSerializer(vacunas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VacunaPacienteViewSet(viewsets.ModelViewSet):
    
   
    queryset = RegistroVacuna.objects.all()
    serializer_class =RegistroVacunaSerializer


class VacunasPorPacienteView(APIView):
    def get(self, request, id_paciente):
        vacunas_paciente = RegistroVacuna.objects.filter(paciente_id=id_paciente).select_related('vacuna','doctor_aprobador__id_usuario')
        
        resultados = []
        for vp in vacunas_paciente:
            resultados.append({
                'id': vp.id, 
                'nombre_vacuna': vp.vacuna.nombre,
                'descripcion_vacuna': vp.vacuna.descripcion,
                'max_dosis': vp.vacuna.max_dosis,
                'fecha_aplicacion': vp.fecha_aplicacion,
                'dosis': vp.dosis,
                'observacion': vp.observacion,
                'aprobado': vp.aprobado,
                'doctor_aprobador': (
                    f"{vp.doctor_aprobador.id_usuario.nombre} {vp.doctor_aprobador.id_usuario.apellido}"
                    if vp.doctor_aprobador else None
                )
            })

        return Response(resultados, status=status.HTTP_200_OK)
    
class EnfermedadPersistenteListView(APIView):
    def get(self, request):
        tipo = request.GET.get('tipo', None)  # Obtener el parámetro 'tipo' de la URL

        if tipo:
            # Filtra las enfermedades persistentes por tipo
            enfermedades = EnfermedadPersistente.objects.filter(tipo=tipo)
        else:
            # Si no se proporciona 'tipo', retorna todas las enfermedades
            enfermedades = EnfermedadPersistente.objects.all()

        serializer = EnfermedadPersistenteSerializer(enfermedades, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PacienteEnfermedadPersistenteViewSet(viewsets.ModelViewSet):
    queryset = PacienteEnfermedadPersistente.objects.all()  # Obtiene todos los registros de enfermedades persistentes
    serializer_class = PacienteEnfermedadPersistenteSerializer  # Usa el serializador de PacienteEnfermedadPersistente


class EnfermedadesPorPacienteView(APIView):
    def get(self, request, id_paciente):
        enfermedades = PacienteEnfermedadPersistente.objects.filter(paciente_id=id_paciente).select_related('enfermedad','doctor_aprobador__id_usuario')
        
        resultados = []
        for e in enfermedades:
            resultados.append({
                'id': e.id, 
                'nombre_enfermedad': e.enfermedad.nombre,
                'Tipo_enfermedad':e.enfermedad.get_tipo_display(),
                'fecha_diagnostico': e.fecha_diagnostico,
                'observacion': e.observacion,
                'aprobado': e.aprobado,
                'doctor_aprobador': (
                    f"{e.doctor_aprobador.id_usuario.nombre} {e.doctor_aprobador.id_usuario.apellido}"
                    if e.doctor_aprobador else None
                )
            })

        return Response(resultados, status=status.HTTP_200_OK)


class DoctoresActivosInactivosView(APIView):
    def get(self, request, id_centromedico):
        # Obtener todos los doctores asociados a este centro médico
        doctores = Doctor.objects.filter(
            id_doctor__in=DoctorCentro.objects.filter(id_centromedico=id_centromedico).values('id_doctor')
        )
        
        # Serializamos la lista de doctores
        serializer = DoctorSerializer(doctores, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ActivarDoctorView(APIView):
    def post(self, request, id_centromedico, id_doctor):
        # Buscar si ya existe una solicitud de DoctorCentro
        try:
            doctor_centro = DoctorCentro.objects.get(id_doctor=id_doctor, id_centromedico=id_centromedico)
        except DoctorCentro.DoesNotExist:
            return Response({"detail": "No se encontró la solicitud del doctor."}, status=status.HTTP_404_NOT_FOUND)

        # Si la solicitud está pendiente, activarla
        if not doctor_centro.aceptado_por_centromedico:
            doctor_centro.aceptado_por_centromedico = True
            doctor_centro.save()
            return Response({"detail": "Doctor activado correctamente."}, status=status.HTTP_200_OK)
        
        return Response({"detail": "El doctor ya está activo en este centro médico."}, status=status.HTTP_400_BAD_REQUEST)
    
class SubirImagenPruebaView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        nombre = request.data.get('nombre')
        imagen = request.FILES.get('imagen')

        print("Datos recibidos: ", request.data)  # Para verificar los datos
        print("Archivos recibidos: ", request.FILES)  # Para verificar los archivos

        if not nombre or not imagen:
            return Response({'error': 'Nombre e imagen son requeridos'}, status=status.HTTP_400_BAD_REQUEST)

        nueva_imagen = PruebaImagen(nombre=nombre, imagen=imagen)
        nueva_imagen.save()

        return Response({'mensaje': 'Imagen subida correctamente'}, status=status.HTTP_201_CREATED)

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        nombre = request.data.get('nombre')
        imagen = request.FILES.get('imagen')

        if not nombre or not imagen:
            return Response({'error': 'Nombre e imagen son requeridos'}, status=status.HTTP_400_BAD_REQUEST)

        nueva_imagen = PruebaImagen(nombre=nombre, imagen=imagen)
        nueva_imagen.save()

        return Response({'mensaje': 'Imagen subida correctamente'}, status=status.HTTP_201_CREATED)
    
@api_view(['PUT'])
def actualizar_foto_perfil(request, id_usuario):
    try:
        usuario = Usuario.objects.get(id_usuario=id_usuario)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    foto = request.FILES.get('foto_perfil')
    if not foto:
        return Response({'error': 'Debe enviar una imagen con el campo "foto_perfil".'}, status=status.HTTP_400_BAD_REQUEST)

    usuario.foto_perfil = foto
    usuario.save()
    return Response({'mensaje': 'Foto de perfil actualizada correctamente.'}, status=status.HTTP_200_OK)



class MedicamentoCronicoListView(APIView):
    def get(self, request):
        # Obtenemos todos los medicamentos crónicos
        medicamentos = MedicamentoCronico.objects.all()
        # Serializamos los medicamentos
        serializer = MedicamentoCronicoSerializer(medicamentos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PacienteMedicamentoCronicoViewSet(viewsets.ModelViewSet):
    queryset = PacienteMedicamentoCronico.objects.all()
    serializer_class = PacienteMedicamentoCronicoSerializer

class TratamientosCronicosPorPacienteView(APIView):
    def get(self, request, id_paciente):
        tratamientos = PacienteMedicamentoCronico.objects.filter(
            id_paciente=id_paciente
        ).select_related('id_medicamento_cronico', 'doctor_aprobador__id_usuario')

        resultados = []
        for t in tratamientos:
            resultados.append({
                'id':t.id,
                'nombre_medicamento': t.id_medicamento_cronico.nombre,
                'descripcion_medicamento': t.id_medicamento_cronico.descripcion,
                'fecha_inicio': t.fecha_inicio,
                'dosis': t.dosis,
                'frecuencia': t.frecuencia,
                'observaciones': t.observaciones,
                'aprobado': t.aprobado,
                'doctor_aprobador': (
                    f"{t.doctor_aprobador.id_usuario.nombre} {t.doctor_aprobador.id_usuario.apellido}"
                    if t.doctor_aprobador else None
                )
            })

        return Response(resultados, status=status.HTTP_200_OK)

class SubirDocumentoView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
        serializer = DocumentoEscaneadoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"mensaje": "PDF subido correctamente", "data": serializer.data})
        return Response(serializer.errors, status=400)
    


class ExamenLaboratorioView(APIView):
    def post(self, request):
        serializer = ExamenLaboratorioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, paciente_id):
        examenes = ExamenLaboratorio.objects.filter(paciente_id=paciente_id).order_by('-fecha_realizacion')
        serializer = ExamenLaboratorioSerializer(examenes, many=True)
        return Response(serializer.data)
    
class ExamenlabImagenologiaView(APIView):
    def post(self, request):
        serializer = ExamenImagenologiaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, paciente_id):
        examenes = ExamenLabImagenologia.objects.filter(paciente_id=paciente_id).order_by('-fecha_realizacion')
        serializer = ExamenImagenologiaSerializer(examenes, many=True)
        return Response(serializer.data)

import cv2
import numpy as np
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def procesar_documento(request):
    if request.method != 'POST':
        return HttpResponse("Método no permitido", status=405)

    if 'imagen' not in request.FILES:
        return HttpResponse("No se envió imagen", status=400)

    file = request.FILES['imagen']
    image_bytes = file.read()

    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if image is None:
        return HttpResponse("Imagen inválida o corrupta", status=400)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Aplicar CLAHE para mejorar contraste local y evitar pérdida de detalles
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)

    # Umbral binario con un valor bajo para atrapar detalles finos
    _, thresh = cv2.threshold(enhanced, 90, 255, cv2.THRESH_BINARY)

    # Invertir para que letras sean negras y fondo blanco
    thresh = cv2.bitwise_not(thresh)

    # Aplicar filtro mediana para reducir ruido manteniendo bordes
    denoised = cv2.medianBlur(thresh, 3)

    # Dilatar suavemente para reforzar letras sin perder detalle
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    dilated = cv2.dilate(denoised, kernel, iterations=1)

    # Invertir nuevamente para que letras negras y fondo blanco
    result = cv2.bitwise_not(dilated)

    _, jpeg = cv2.imencode('.jpg', result)
    return HttpResponse(jpeg.tobytes(), content_type="image/jpeg")

# views.py
from rest_framework.decorators import api_view


@api_view(['GET'])
def proxima_dosis(request, paciente_id, vacuna_id):
    registros = RegistroVacuna.objects.filter(paciente_id=paciente_id, vacuna_id=vacuna_id).order_by('dosis')
    if registros.exists():
        ultima_dosis = registros.last().dosis
        return Response({"proxima_dosis": ultima_dosis + 1})
    return Response({"proxima_dosis": 1})



from django.db.models import Max

@api_view(['GET'])
def ultimas_dosis_por_paciente(request, paciente_id):
    # Obtener la última dosis por cada vacuna
    subquery = RegistroVacuna.objects.filter(paciente_id=paciente_id)
    ultimas = subquery.values('vacuna').annotate(ultima_dosis=Max('dosis'))

    resultado = []
    for entry in ultimas:
        vacuna_id = entry['vacuna']
        dosis = entry['ultima_dosis']
        registro = RegistroVacuna.objects.select_related('vacuna', 'doctor_aprobador__id_usuario').get(
            paciente_id=paciente_id,
            vacuna_id=vacuna_id,
            dosis=dosis
        )

        resultado.append({
            'id': registro.id,
            'nombre_vacuna': registro.vacuna.nombre,
            'descripcion_vacuna': registro.vacuna.descripcion,
            'max_dosis': registro.vacuna.max_dosis,
            'fecha_aplicacion': registro.fecha_aplicacion,
            'dosis': registro.dosis,
            'observacion': registro.observacion,
            'aprobado': registro.aprobado,
            'doctor_aprobador': (
                f"{registro.doctor_aprobador.id_usuario.nombre} {registro.doctor_aprobador.id_usuario.apellido}"
                if registro.doctor_aprobador else None
            )
        })

    return Response(resultado)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TratamientoActual, SeguimientoTratamiento
from .serializers import TratamientoActualSerializer, SeguimientoTratamientoSerializer

@api_view(['GET'])
def tratamientos_por_paciente(request, paciente_id):
    tratamientos = TratamientoActual.objects.filter(paciente_id=paciente_id).select_related('medicamento').order_by('-created_at')

    resultados = []
    for t in tratamientos:
        resultados.append({
            'id': t.id,
            'descripcion': t.descripcion,
            'fecha_inicio': t.fecha_inicio,
            'fecha_fin': t.fecha_fin,
            'finalizado': t.finalizado,
            'frecuencia': t.frecuencia,
            'created_at': t.created_at,
            'updated_at': t.updated_at,
            'paciente': t.paciente_id,
            'medicamento': t.medicamento_id,
            'nombre_medicamento': t.medicamento.nombre_comercial if t.medicamento else None,
            'dosis':t.medicamento.concentracion if t.medicamento else None,
            'via': t.medicamento.via_administracion if t.medicamento else None,
            'doctor': t.doctor_id,
            'nombre_doctor': (
                f"{t.doctor.id_usuario.nombre} {t.doctor.id_usuario.apellido}"
                if t.doctor and t.doctor.id_usuario else None
            )
        })

    return Response(resultados)



@api_view(['POST'])
def crear_tratamiento(request):
    paciente_id = request.data.get('paciente')
    medicamento_id = request.data.get('medicamento')

    # Validación mínima necesaria para la restricción
    if not paciente_id or not medicamento_id:
        return Response({'error': 'El paciente y el medicamento son obligatorios para validar duplicación.'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Restricción: no permitir duplicados no finalizados
    tratamiento_existente = TratamientoActual.objects.filter(
        paciente_id=paciente_id,
        medicamento_id=medicamento_id,
        finalizado=False
    ).exists()

    if tratamiento_existente:
        return Response(
            {'error': 'Ya existe un tratamiento activo con este medicamento para el paciente.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Continuar con la creación
    serializer = TratamientoActualSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
def finalizar_tratamiento(request, tratamiento_id):
    try:
        tratamiento = TratamientoActual.objects.get(id=tratamiento_id)
    except TratamientoActual.DoesNotExist:
        return Response({'error': 'No encontrado'}, status=404)
    
    tratamiento.finalizado = True
    tratamiento.fecha_fin = request.data.get('fecha_fin')
    tratamiento.save()
    return Response({'mensaje': 'Tratamiento finalizado'})


from rest_framework.decorators import api_view, parser_classes


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def agregar_seguimiento(request):
    serializer = SeguimientoTratamientoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    print("Errores:", serializer.errors)  # Agregado para depuración
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# views.py


@api_view(['GET'])
def obtener_seguimientos(request, tratamiento_id):
    seguimientos = SeguimientoTratamiento.objects.filter(tratamiento_id=tratamiento_id).order_by('-fecha')
    serializer = SeguimientoTratamientoSerializer(seguimientos, many=True)
    return Response(serializer.data)




from .models import Medicamento
from .serializers import MedicamentoSerializer

@api_view(['GET'])
def listar_medicamentos(request):
    tipo = request.GET.get('tipo')
    if tipo:
        medicamentos = Medicamento.objects.filter(tipo__iexact=tipo)
    else:
        medicamentos = Medicamento.objects.all()
    
    serializer = MedicamentoSerializer(medicamentos, many=True)
    return Response(serializer.data)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Paciente, Usuario
from .serializers import PacienteSerializercedula

@api_view(['GET'])
def buscar_paciente_por_cedula(request):
    cedula = request.GET.get('cedula')

    if not cedula:
        return Response({"error": "Debe proporcionar una cédula."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        usuario = Usuario.objects.get(cedula=cedula)
        paciente = Paciente.objects.get(id_usuario=usuario)
        serializer = PacienteSerializercedula(paciente)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario con esa cédula no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    except Paciente.DoesNotExist:
        return Response({"error": "No hay paciente asociado a ese usuario."}, status=status.HTTP_404_NOT_FOUND)


from rest_framework.decorators import action
from django.utils.timezone import now
from .models import DoctorPaciente
from .serializers import DoctorPacienteSerializer

class DoctorPacienteViewSet(viewsets.ModelViewSet):
    queryset = DoctorPaciente.objects.all()
    serializer_class = DoctorPacienteSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['estado'] = 'pendiente'
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def aceptar(self, request, pk=None):
        relacion = self.get_object()
        if relacion.estado != 'pendiente':
            return Response({'detail': 'Ya fue respondida.'}, status=400)

        relacion.estado = 'aceptado'
        relacion.aprobado_en = now()
        relacion.save()
        return Response({'detail': 'Solicitud aceptada.'})

    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        relacion = self.get_object()
        if relacion.estado != 'pendiente':
            return Response({'detail': 'Ya fue respondida.'}, status=400)

        relacion.estado = 'rechazado'
        relacion.save()
        return Response({'detail': 'Solicitud rechazada.'})
