from rest_framework import viewsets, serializers, status
from .models import Usuario
from .serializers import UsuarioSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import authenticate
from rest_framework.response import Response

# ViewSet para el manejo de usuarios
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()  # Obtiene todos los usuarios
    serializer_class = UsuarioSerializer  # Usa el serializador de usuarios
    permission_classes = [AllowAny]  # Permite que cualquiera acceda a este ViewSet (solo para pruebas)
    
    def create(self, request, *args, **kwargs):
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
