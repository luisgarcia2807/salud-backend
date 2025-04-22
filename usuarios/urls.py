from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, CustomTokenObtainPairView, CustomTokenRefreshView

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # Para obtener el token
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),  # Para refrescar el token
]
