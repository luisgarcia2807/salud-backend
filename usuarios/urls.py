from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActivarDoctorView, AlergiasPorPacienteView, DoctorPacienteViewSet, DoctoresActivosInactivosView, EnfermedadPersistenteListView, EnfermedadesPorPacienteView, ExamenLaboratorioView, ExamenlabImagenologiaView, GrupoSanguineoListView, ListaAlergias, MedicamentoCronicoListView, PacienteAlergiaViewSet, PacienteEnfermedadPersistenteViewSet, PacienteMedicamentoCronicoViewSet, PacientePorUsuarioView, SolicitudesPorDoctorAPIView, SolicitudesPorPacienteAPIView, SubirDocumentoView, SubirImagenPruebaView, TratamientosCronicosPorPacienteView, UsuarioDetailView, UsuarioViewSet, CustomTokenObtainPairView, CustomTokenRefreshView, VacunaListView, VacunaPacienteViewSet, VacunasPorPacienteView, actualizar_foto_perfil, buscar_paciente_por_cedula, listar_medicamentos, procesar_documento, proxima_dosis, ultimas_dosis_por_paciente
from .views import CentroMedicoListView, EspecialidadListView
from . import views


router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'pacientes-alergias', PacienteAlergiaViewSet)  # Registrar el viewset de PacienteAlergia
router.register(r'vacunas-pacientes', VacunaPacienteViewSet, basename='vacunapaciente')
router.register(r'pacientes_enfermedades', PacienteEnfermedadPersistenteViewSet, basename='pacienteenfermedad')
router.register(r'paciente_medicamento_cronico', PacienteMedicamentoCronicoViewSet)
router.register(r'doctor-paciente', DoctorPacienteViewSet, basename='doctor-paciente')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # Para obtener el token
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),  # Para refrescar el token
    path('api/centros_medicos/', CentroMedicoListView.as_view(), name='centros_medicos_list'),
    path('api/especialidades/', EspecialidadListView.as_view(), name='especialidades_list'),
    path('api/grupos-sanguineos/', GrupoSanguineoListView.as_view(), name='grupo_sanguineo_list'),
    path('api/usuario/<int:id_usuario>/', UsuarioDetailView.as_view(), name='usuario-detail'),
    path('api/pacientes/por-usuario/<int:id_usuario>/', PacientePorUsuarioView.as_view(), name='paciente-por-usuario'),
    path('api/alergias/', ListaAlergias.as_view(), name='lista-alergias'),
    path('api/pacientes/<int:id_paciente>/alergias/', AlergiasPorPacienteView.as_view(), name='alergias-por-paciente'),
    path('api/vacunas/', VacunaListView.as_view(), name='vacuna_lista'),
    path('api/pacientes/<int:id_paciente>/vacunas/', VacunasPorPacienteView.as_view(), name='vacunas-por-paciente'),
    path('api/enfermedades-persistentes/', EnfermedadPersistenteListView.as_view(), name='list_enfermedades_persistentes'),
    path('api/enfermedades/<int:id_paciente>/paciente/', EnfermedadesPorPacienteView.as_view(), name='enfermedades_por_paciente'),
    path('api/centro-medico/<int:id_centromedico>/doctores/', DoctoresActivosInactivosView.as_view(), name='doctores_activos_inactivos'),
    path('api/centro-medico/<int:id_centromedico>/activar-doctor/<int:id_doctor>/', ActivarDoctorView.as_view(), name='activar_doctor'),
    path('api/subir-imagen/', SubirImagenPruebaView.as_view(), name='subir-imagen'),
    path('api/usuarios/<int:id_usuario>/actualizar-foto/', actualizar_foto_perfil, name='actualizar_foto'),
    path('api/medicamentos/', MedicamentoCronicoListView.as_view(), name='medicamentos_list'),
    path('api/tratamientos-cronicos/<int:id_paciente>/', TratamientosCronicosPorPacienteView.as_view(), name='tratamientos_cronicos_por_paciente'),
    path('api/subir-pdf/', SubirDocumentoView.as_view(), name='subir-pdf'),
    path('api/examenes/', ExamenLaboratorioView.as_view(), name='subir_examen'),
    path('api/examenes/<int:paciente_id>/', ExamenLaboratorioView.as_view(), name='listar_examenes_paciente'),
    path('api/procesar_documento/', procesar_documento, name='procesar_documento'),
    path('api/imagenologia/', ExamenlabImagenologiaView.as_view(), name='subir_examen'),
    path('api/imagenologia/<int:paciente_id>/', ExamenlabImagenologiaView.as_view(), name='listar_examenes_paciente'),
    path('api/proxima-dosis/<int:paciente_id>/<int:vacuna_id>/', proxima_dosis),
    path('api/paciente/<int:paciente_id>/ultimas-vacunas/', ultimas_dosis_por_paciente),
    path('api/paciente/<int:paciente_id>/tratamientos/', views.tratamientos_por_paciente),
    path('api/tratamiento/nuevo/', views.crear_tratamiento),
    path('api/tratamiento/<int:tratamiento_id>/finalizar/', views.finalizar_tratamiento),
    path('api/tratamiento/seguimiento/nuevo/', views.agregar_seguimiento),
    path('api/medicamentosfrecuente/', listar_medicamentos),
    path('api/tratamiento/<int:tratamiento_id>/seguimientos/', views.obtener_seguimientos),
    path('api/paciente/por-cedula/', buscar_paciente_por_cedula),
    path('api/solicitudes/doctor/<int:doctor_id>/', SolicitudesPorDoctorAPIView.as_view()),
    path('api/solicitudes/paciente/<int:paciente_id>/', SolicitudesPorPacienteAPIView.as_view()),
   



]

