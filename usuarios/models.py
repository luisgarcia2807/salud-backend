from django.db import models
from django.contrib.auth.models import AbstractUser

class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

class Usuario(AbstractUser):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=15)
    estado = models.BooleanField(default=True)
    id_rol = models.ForeignKey('Rol', on_delete=models.CASCADE, default=1)

    # Agregar campo is_active
    is_active = models.BooleanField(default=True)  # Este campo controla si el usuario está activo o no

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'telefono']

    def save(self, *args, **kwargs):
        if not self.pk and self.password:
            self.set_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    

    

