from rest_framework import serializers
from .models import Usuario
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)

    class Meta:
        model = Usuario
        fields = ['id_usuario', 'nombre', 'apellido', 'cedula', 'email', 'telefono', 'fecha_nacimiento', 'estado', 'id_rol', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        if 'username' not in validated_data or not validated_data['username']:
            validated_data['username'] = validated_data['email']
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError("Debe proporcionar un email y una contraseña.")

        # Autenticación usando el email como username
        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError("Credenciales inválidas.")

        data = super().validate(attrs)

        data.update({
            "id_usuario": user.id_usuario,
            "email": user.email,
            "nombre": user.nombre,
            "apellido": user.apellido
        })
        return data
