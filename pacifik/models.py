from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json


class Area(models.Model):
    """Modelo para las áreas comunes del edificio"""
    nombre = models.CharField(max_length=100, unique=True)
    instrucciones = models.TextField(help_text="Instrucciones de uso del área")
    cupos_por_horario = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Número de cupos disponibles por horario"
    )
    
    # Horarios permitidos almacenados como JSON
    # Formato: {"lunes": ["08:00-09:00", "09:00-10:00"], "martes": [...]}
    horarios_permitidos = models.JSONField(
        default=dict,
        help_text="Horarios permitidos por día de la semana"
    )
    
    # Duraciones de slot permitidas (en horas)
    duraciones_permitidas = models.JSONField(
        default=list,
        help_text="Lista de duraciones permitidas en horas [1, 2, 3, 4]"
    )
    
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Área Común'
        verbose_name_plural = 'Áreas Comunes'

    def __str__(self):
        return self.nombre

    def get_horarios_para_dia(self, dia_semana):
        """
        Retorna los horarios disponibles para un día específico
        dia_semana: 'lunes', 'martes', etc.
        """
        if isinstance(self.horarios_permitidos, str):
            horarios = json.loads(self.horarios_permitidos)
        else:
            horarios = self.horarios_permitidos
        
        return horarios.get(dia_semana.lower(), [])


class UserProfile(models.Model):
    """Extensión del modelo User para información adicional"""
    
    ROLE_CHOICES = [
        ('resident', 'Residente'),
        ('supervisor', 'Supervisor'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile_pacifik')
    numero_departamento = models.CharField(max_length=10)
    es_administrador = models.BooleanField(default=False)
    
    # Nuevos campos de rol y permisos
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='resident',
        help_text="Rol del usuario en el sistema"
    )
    can_make_reservations = models.BooleanField(
        default=True,
        help_text="Si el usuario puede crear reservas"
    )
    can_view_all_reservations = models.BooleanField(
        default=False,
        help_text="Si el usuario puede ver todas las reservas del edificio"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

    def __str__(self):
        return f"{self.user.get_full_name()} - Dpto {self.numero_departamento} ({self.get_role_display()})"
    
    def is_supervisor(self):
        """Verifica si el usuario es supervisor"""
        return self.role == 'supervisor'
    
    def is_resident(self):
        """Verifica si el usuario es residente"""
        return self.role == 'resident'
    
    def can_reserve(self):
        """Verifica si el usuario puede hacer reservas"""
        return self.can_make_reservations and not self.is_supervisor()
    
    def get_permissions(self):
        """Retorna un diccionario con todos los permisos del usuario"""
        return {
            'can_make_reservations': self.can_reserve(),
            'can_view_all_reservations': self.can_view_all_reservations,
            'role': self.role,
            'is_supervisor': self.is_supervisor(),
            'is_resident': self.is_resident()
        }


class Reserva(models.Model):
    """Modelo para las reservas de áreas comunes"""
    
    ESTADO_CHOICES = [
        ('reservado', 'Reservado'),
        ('cancelado', 'Cancelado'),
        ('completado', 'Completado'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservas_pacifik')
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='reservas')
    fecha = models.DateField()
    horario_inicio = models.TimeField()
    horario_fin = models.TimeField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='reservado')
    terminos_aceptados = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha', '-horario_inicio']
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        # Constraint para evitar duplicados de usuario-area-fecha en el mismo horario
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'area', 'fecha', 'horario_inicio'],
                condition=models.Q(estado='reservado'),
                name='unique_reservation_per_user_area_date_time'
            )
        ]

    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.area.nombre} - {self.fecha} {self.horario_inicio}-{self.horario_fin}"

    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validar que la fecha no sea pasada (usar zona horaria local)
        if self.fecha < timezone.localtime().date():
            raise ValidationError("No se pueden hacer reservas para fechas pasadas")
        
        # Validar que el horario de fin sea mayor al de inicio
        if self.horario_fin <= self.horario_inicio:
            raise ValidationError("El horario de fin debe ser mayor al de inicio")
        
        # Validar que los términos estén aceptados
        if not self.terminos_aceptados:
            raise ValidationError("Debe aceptar los términos y condiciones")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def duracion_horas(self):
        """Calcula la duración de la reserva en horas"""
        from datetime import datetime, timedelta
        
        inicio = datetime.combine(self.fecha, self.horario_inicio)
        fin = datetime.combine(self.fecha, self.horario_fin)
        
        # Si el horario fin es menor, asumimos que es del día siguiente
        if fin < inicio:
            fin += timedelta(days=1)
        
        duracion = fin - inicio
        return duracion.total_seconds() / 3600

    def esta_activa(self):
        """Verifica si la reserva está activa (no cancelada y fecha/hora no pasada)"""
        if self.estado == 'cancelado':
            return False
        
        ahora = timezone.now()
        fecha_hora_inicio = timezone.make_aware(
            timezone.datetime.combine(self.fecha, self.horario_inicio)
        )
        
        return fecha_hora_inicio > ahora
