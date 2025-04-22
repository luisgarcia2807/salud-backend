# salud_backend/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from usuarios.views import CustomTokenObtainPairView  # Asegúrate de importar tu vista personalizada

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # Usa la vista personalizada
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Para refrescar el token
    path('usuarios/', include('usuarios.urls')),  # Rutas de tu aplicación de usuarios
    # Otras rutas de tu aplicación...
]
