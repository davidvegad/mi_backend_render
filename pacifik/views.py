from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from collections import defaultdict
import calendar
import os

from .models import Area, UserProfile, Reserva
from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer, AreaSerializer,
    ReservaSerializer, ReservaCreateSerializer, ReservaListSerializer,
    DisponibilidadSerializer, HorarioDisponibleSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    """Vista para registro de usuarios"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'Usuario registrado exitosamente',
            'user_id': user.id,
            'email': user.email
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveAPIView):
    """Vista para obtener el perfil del usuario autenticado"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(
            user=self.request.user,
            defaults={'numero_departamento': ''}
        )
        return profile


class AreaListCreateView(generics.ListCreateAPIView):
    """Vista para listar y crear áreas comunes"""
    queryset = Area.objects.filter(activa=True)
    serializer_class = AreaSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]


class AreaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para detalles, actualizar y eliminar áreas"""
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        # Soft delete
        area = self.get_object()
        area.activa = False
        area.save()
        return Response({'message': 'Área desactivada exitosamente'})


class ReservaListCreateView(generics.ListCreateAPIView):
    """Vista para listar reservas del usuario y crear nuevas"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReservaCreateSerializer
        return ReservaListSerializer
    
    def get_queryset(self):
        return Reserva.objects.filter(
            usuario=self.request.user
        ).select_related('area', 'usuario__profile_pacifik')
    
    def create(self, request, *args, **kwargs):
        """Crear nueva reserva con validación de permisos"""
        # Verificar si el usuario tiene permisos para hacer reservas
        try:
            profile = request.user.profile_pacifik
            if not profile.can_reserve():
                return Response({
                    'error': 'No tienes permisos para crear reservas',
                    'detail': 'Tu cuenta está configurada solo para visualización. Contacta al administrador si necesitas hacer una reserva.',
                    'user_role': profile.role
                }, status=status.HTTP_403_FORBIDDEN)
        except AttributeError:
            return Response({
                'error': 'Perfil de usuario no configurado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return super().create(request, *args, **kwargs)


class ReservaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para detalles y manejo de reservas individuales"""
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Reserva.objects.filter(usuario=self.request.user)

    def destroy(self, request, *args, **kwargs):
        # Cancelar reserva en lugar de eliminarla
        reserva = self.get_object()
        reserva.estado = 'cancelado'
        reserva.save()
        return Response({'message': 'Reserva cancelada exitosamente'})
    


class AdminReservaListView(generics.ListAPIView):
    """Vista para que los administradores vean todas las reservas"""
    serializer_class = ReservaListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Verificar si el usuario es administrador
        if not hasattr(self.request.user, 'profile_pacifik') or not self.request.user.profile_pacifik.es_administrador:
            return Reserva.objects.none()
        
        queryset = Reserva.objects.select_related('area', 'usuario__profile_pacifik')
        
        # Filtros opcionales
        area_id = self.request.query_params.get('area')
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        departamento = self.request.query_params.get('departamento')
        
        if area_id:
            queryset = queryset.filter(area_id=area_id)
        
        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)
        
        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)
        
        if departamento:
            queryset = queryset.filter(usuario__profile_pacifik__numero_departamento=departamento)
        
        return queryset


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def consultar_disponibilidad(request):
    """Endpoint para consultar disponibilidad de horarios"""
    # Verificar permisos para consultar disponibilidad
    try:
        profile = request.user.profile_pacifik
        if not profile.can_reserve():
            return Response({
                'error': 'No tienes permisos para consultar disponibilidad',
                'detail': 'Solo los usuarios que pueden hacer reservas pueden consultar disponibilidad.',
                'user_role': profile.role
            }, status=status.HTTP_403_FORBIDDEN)
    except AttributeError:
        return Response({
            'error': 'Perfil de usuario no configurado'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = DisponibilidadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    area_id = serializer.validated_data['area_id']
    fecha = serializer.validated_data['fecha']
    
    try:
        area = Area.objects.get(id=area_id, activa=True)
    except Area.DoesNotExist:
        return Response({'error': 'Área no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    # Obtener día de la semana
    dias_semana = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
    dia_semana = dias_semana[fecha.weekday()]
    
    # Obtener horarios permitidos para este día
    horarios_permitidos = area.get_horarios_para_dia(dia_semana)
    
    if not horarios_permitidos:
        return Response({
            'area': area.nombre,
            'fecha': fecha,
            'horarios_disponibles': []
        })
    
    # Obtener reservas existentes para esta fecha y área
    reservas_existentes = Reserva.objects.filter(
        area=area,
        fecha=fecha,
        estado='reservado'
    )
    
    # Calcular disponibilidad para cada horario
    horarios_disponibles = []
    
    for horario_str in horarios_permitidos:
        try:
            inicio_str, fin_str = horario_str.split('-')
            horario_inicio = datetime.strptime(inicio_str.strip(), '%H:%M').time()
            horario_fin = datetime.strptime(fin_str.strip(), '%H:%M').time()
            
            # Contar reservas que se solapan con este horario
            reservas_solapadas = reservas_existentes.filter(
                horario_inicio__lt=horario_fin,
                horario_fin__gt=horario_inicio
            ).count()
            
            cupos_disponibles = max(0, area.cupos_por_horario - reservas_solapadas)
            
            horarios_disponibles.append({
                'horario_inicio': horario_inicio,
                'horario_fin': horario_fin,
                'cupos_disponibles': cupos_disponibles,
                'cupos_totales': area.cupos_por_horario
            })
            
        except ValueError:
            continue  # Saltar horarios con formato inválido
    
    return Response({
        'area': area.nombre,
        'fecha': fecha,
        'horarios_disponibles': horarios_disponibles
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estadisticas_usuario(request):
    """Estadísticas del usuario actual"""
    usuario = request.user
    
    # Contar reservas por estado
    total_reservas = Reserva.objects.filter(usuario=usuario).count()
    reservas_activas = Reserva.objects.filter(usuario=usuario, estado='reservado').count()
    reservas_completadas = Reserva.objects.filter(usuario=usuario, estado='completado').count()
    reservas_canceladas = Reserva.objects.filter(usuario=usuario, estado='cancelado').count()
    
    # Próximas reservas
    proximas_reservas = Reserva.objects.filter(
        usuario=usuario,
        estado='reservado',
        fecha__gte=timezone.localtime().date()
    ).order_by('fecha', 'horario_inicio')[:5]
    
    return Response({
        'total_reservas': total_reservas,
        'reservas_activas': reservas_activas,
        'reservas_completadas': reservas_completadas,
        'reservas_canceladas': reservas_canceladas,
        'proximas_reservas': ReservaListSerializer(proximas_reservas, many=True).data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def todas_las_reservas(request):
    """Lista todas las reservas del edificio con paginación y filtros optimizados"""
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    # Parámetros de paginación
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    # Filtros opcionales
    area_id = request.GET.get('area')
    fecha = request.GET.get('fecha')
    estado = request.GET.get('estado')
    departamento = request.GET.get('departamento')
    
    # Query base con select_related para optimizar
    reservas = Reserva.objects.select_related('usuario', 'area', 'usuario__profile_pacifik')
    
    # Aplicar filtros
    if area_id and area_id.strip():
        reservas = reservas.filter(area_id=area_id)
    if fecha and fecha.strip():
        reservas = reservas.filter(fecha=fecha)
    if estado and estado.strip():
        reservas = reservas.filter(estado=estado)
    if departamento and departamento.strip():
        reservas = reservas.filter(
            usuario__profile_pacifik__numero_departamento__icontains=departamento
        )
    
    # Ordenar: si es fecha de hoy y estado reservado, ordenar por hora ascendente
    # En otros casos, ordenar por fecha y hora descendente
    fecha_hoy = timezone.localtime().date()
    if (fecha and fecha.strip() == str(fecha_hoy) and 
        estado and estado.strip() == 'reservado'):
        reservas = reservas.order_by('horario_inicio')  # orden ascendente por hora para hoy
    else:
        reservas = reservas.order_by('-fecha', '-horario_inicio')  # orden descendente para otros casos
    
    # Aplicar paginación
    paginator = Paginator(reservas, page_size)
    
    # Validar número de página
    if page < 1:
        page = 1
    if page > paginator.num_pages and paginator.num_pages > 0:
        page = paginator.num_pages
    
    page_obj = paginator.get_page(page)
    
    return Response({
        'reservas': ReservaListSerializer(page_obj.object_list, many=True).data,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'page_size': page_size,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'next_page': page + 1 if page_obj.has_next() else None,
            'previous_page': page - 1 if page_obj.has_previous() else None
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])  # Temporal - en producción usar API key
def auto_complete_reservations_webhook(request):
    """Endpoint para auto-completar reservas (para cron externos)"""
    from django.core.management import call_command
    from io import StringIO
    
    # Verificar API key desde Authorization header
    auth_header = request.headers.get('Authorization', '')
    api_key = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else ''
    expected_key = os.environ.get('CRON_API_KEY', 'default-key')
    
    if not api_key or api_key != expected_key:
        return Response({
            'error': 'API Key inválida o faltante',
            'detail': 'Incluye Authorization: Bearer <tu-api-key> en el header'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        # Capturar output del comando
        out = StringIO()
        call_command('complete_past_reservations', stdout=out)
        output = out.getvalue()
        
        return Response({
            'success': True,
            'message': 'Comando ejecutado exitosamente',
            'output': output
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IsAdminUser(permissions.BasePermission):
    """Permiso personalizado para verificar si el usuario es administrador"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and
            hasattr(request.user, 'profile_pacifik') and
            request.user.profile_pacifik.es_administrador
        )
