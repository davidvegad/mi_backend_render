from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Area, UserProfile, Reserva


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para registro de usuarios"""
    password = serializers.CharField(write_only=True, min_length=8)
    numero_departamento = serializers.CharField(max_length=10)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'numero_departamento']
        extra_kwargs = {
            'username': {'required': False},  # Lo generamos automáticamente
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value

    def create(self, validated_data):
        numero_departamento = validated_data.pop('numero_departamento')
        
        # Crear usuario
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        
        # Crear perfil
        UserProfile.objects.create(
            user=user,
            numero_departamento=numero_departamento
        )
        
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para el perfil del usuario"""
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['email', 'first_name', 'last_name', 'full_name', 'numero_departamento', 'es_administrador']

    def get_full_name(self, obj):
        return obj.user.get_full_name()


class AreaSerializer(serializers.ModelSerializer):
    """Serializer para las áreas comunes"""
    
    class Meta:
        model = Area
        fields = [
            'id', 'nombre', 'instrucciones', 'cupos_por_horario',
            'horarios_permitidos', 'duraciones_permitidas', 'activa',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_horarios_permitidos(self, value):
        """Validar formato de horarios permitidos"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Los horarios deben ser un diccionario")
        
        dias_validos = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        
        for dia, horarios in value.items():
            if dia.lower() not in dias_validos:
                raise serializers.ValidationError(f"Día inválido: {dia}")
            
            if not isinstance(horarios, list):
                raise serializers.ValidationError(f"Los horarios para {dia} deben ser una lista")
            
            for horario in horarios:
                if not isinstance(horario, str) or '-' not in horario:
                    raise serializers.ValidationError(f"Formato de horario inválido: {horario}")
        
        return value

    def validate_duraciones_permitidas(self, value):
        """Validar duraciones permitidas"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Las duraciones deben ser una lista")
        
        for duracion in value:
            if not isinstance(duracion, (int, float)) or duracion <= 0:
                raise serializers.ValidationError("Las duraciones deben ser números positivos")
        
        return value


class ReservaSerializer(serializers.ModelSerializer):
    """Serializer para las reservas"""
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    usuario_departamento = serializers.SerializerMethodField()
    area_nombre = serializers.CharField(source='area.nombre', read_only=True)
    duracion_horas = serializers.ReadOnlyField()
    esta_activa = serializers.ReadOnlyField()
    
    def get_usuario_departamento(self, obj):
        """Obtener departamento del usuario de forma segura"""
        try:
            return obj.usuario.profile_pacifik.numero_departamento
        except:
            return "N/A"

    class Meta:
        model = Reserva
        fields = [
            'id', 'usuario', 'usuario_nombre', 'usuario_departamento',
            'area', 'area_nombre', 'fecha', 'horario_inicio', 'horario_fin',
            'estado', 'terminos_aceptados', 'duracion_horas', 'esta_activa',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['usuario', 'created_at', 'updated_at']

    def validate_fecha(self, value):
        """Validar que la fecha no sea pasada"""
        if value < timezone.localtime().date():
            raise serializers.ValidationError("No se pueden hacer reservas para fechas pasadas")
        return value

    def validate_terminos_aceptados(self, value):
        """Validar que los términos estén aceptados"""
        if not value:
            raise serializers.ValidationError("Debe aceptar los términos y condiciones")
        return value

    def validate(self, data):
        """Validaciones cruzadas"""
        # Validar que el horario de fin sea mayor al de inicio
        if data['horario_fin'] <= data['horario_inicio']:
            raise serializers.ValidationError("El horario de fin debe ser mayor al de inicio")
        
        area = data['area']
        fecha = data['fecha']
        horario_inicio = data['horario_inicio']
        horario_fin = data['horario_fin']
        
        # Obtener el usuario del contexto
        usuario = self.context['request'].user
        
        # Validar que el usuario no tenga otra reserva activa para la misma área
        # (solo reservas de hoy en adelante)
        hoy = timezone.localtime().date()
        reservas_activas_usuario = Reserva.objects.filter(
            usuario=usuario,
            area=area,
            estado='reservado',
            fecha__gte=hoy  # Solo considerar reservas de hoy en adelante
        )
        
        # Si estamos editando, excluir la reserva actual
        if self.instance:
            reservas_activas_usuario = reservas_activas_usuario.exclude(id=self.instance.id)
        
        if reservas_activas_usuario.exists():
            raise serializers.ValidationError({
                'area': f'Ya tienes una reserva activa para {area.nombre}. '
                       'Debes completar o cancelar tu reserva anterior antes de hacer una nueva.'
            })
        
        # Validar disponibilidad de cupos para el horario específico
        reservas_solapadas = Reserva.objects.filter(
            area=area,
            fecha=fecha,
            estado='reservado'
        ).filter(
            # Reservas que se solapan: inicio < fin_nuevo AND fin > inicio_nuevo
            horario_inicio__lt=horario_fin,
            horario_fin__gt=horario_inicio
        )
        
        # Si estamos editando, excluir la reserva actual
        if self.instance:
            reservas_solapadas = reservas_solapadas.exclude(id=self.instance.id)
        
        if reservas_solapadas.count() >= area.cupos_por_horario:
            raise serializers.ValidationError({
                'horario': "No hay cupos disponibles para este horario. Por favor selecciona otro horario."
            })
        
        return data

    def create(self, validated_data):
        # Asignar el usuario actual
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)


class ReservaCreateSerializer(ReservaSerializer):
    """Serializer específico para crear reservas"""
    
    class Meta(ReservaSerializer.Meta):
        fields = [
            'area', 'fecha', 'horario_inicio', 'horario_fin', 'terminos_aceptados'
        ]


class ReservaListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listar reservas"""
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    usuario_departamento = serializers.SerializerMethodField()
    area_nombre = serializers.CharField(source='area.nombre', read_only=True)
    
    def get_usuario_departamento(self, obj):
        """Obtener departamento del usuario de forma segura"""
        try:
            return obj.usuario.profile_pacifik.numero_departamento
        except:
            return "N/A"

    class Meta:
        model = Reserva
        fields = [
            'id', 'usuario_nombre', 'usuario_departamento', 'area_nombre',
            'fecha', 'horario_inicio', 'horario_fin', 'estado', 'created_at'
        ]


class DisponibilidadSerializer(serializers.Serializer):
    """Serializer para consultar disponibilidad de horarios"""
    area_id = serializers.IntegerField()
    fecha = serializers.DateField()
    
    def validate_fecha(self, value):
        # Obtener la fecha actual en la zona horaria local (Lima)
        fecha_actual_lima = timezone.localtime().date()
        if value < fecha_actual_lima:
            raise serializers.ValidationError("No se puede consultar disponibilidad para fechas pasadas")
        return value

    def validate_area_id(self, value):
        try:
            Area.objects.get(id=value, activa=True)
        except Area.DoesNotExist:
            raise serializers.ValidationError("Área no encontrada o inactiva")
        return value


class HorarioDisponibleSerializer(serializers.Serializer):
    """Serializer para representar horarios disponibles"""
    horario_inicio = serializers.TimeField()
    horario_fin = serializers.TimeField()
    cupos_disponibles = serializers.IntegerField()
    cupos_totales = serializers.IntegerField()