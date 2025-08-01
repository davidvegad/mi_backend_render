# Vistas para el sistema de evaluación trimestral
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q
from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import os

from .models_evaluation import (
    EvaluationRole, ObjectiveCategory, Objective, Quarter, 
    EmployeeEvaluation, EvaluationObjective, EvaluationAttachment
)
from .serializers_evaluation import (
    EvaluationRoleSerializer, ObjectiveCategorySerializer, ObjectiveSerializer,
    ObjectivesByRoleSerializer, QuarterSerializer, EmployeeEvaluationSerializer,
    EmployeeEvaluationCreateSerializer, EvaluationObjectiveSerializer,
    EvaluationAttachmentSerializer, EvaluationSummarySerializer, UserSerializer
)


class EvaluationRoleViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar roles de evaluación"""
    queryset = EvaluationRole.objects.all()
    serializer_class = EvaluationRoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            # Filtrar por activos por defecto
            is_active = self.request.query_params.get('is_active', 'true')
            if is_active.lower() == 'true':
                queryset = queryset.filter(is_active=True)
        return queryset
    
    @action(detail=True, methods=['get'])
    def objectives(self, request, pk=None):
        """Obtener objetivos agrupados por categoría para un rol específico"""
        role = self.get_object()
        serializer = ObjectivesByRoleSerializer(role)
        return Response(serializer.data)


class ObjectiveCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet de solo lectura para categorías de objetivos"""
    queryset = ObjectiveCategory.objects.all()
    serializer_class = ObjectiveCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class ObjectiveViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar objetivos"""
    queryset = Objective.objects.all()
    serializer_class = ObjectiveSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['role', 'category', 'is_active']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por rol
        role_id = self.request.query_params.get('role')
        if role_id:
            queryset = queryset.filter(role_id=role_id)
        
        # Filtro por categoría
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name=category)
        
        # Filtro por activos
        is_active = self.request.query_params.get('is_active', 'true')
        if is_active.lower() == 'true':
            queryset = queryset.filter(is_active=True)
            
        return queryset.order_by('role', 'category__order', 'title')


class QuarterViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar trimestres"""
    queryset = Quarter.objects.all()
    serializer_class = QuarterSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Obtener el trimestre activo actual"""
        active_quarter = Quarter.objects.filter(is_active=True).first()
        if active_quarter:
            serializer = self.get_serializer(active_quarter)
            return Response(serializer.data)
        return Response({'detail': 'No hay trimestre activo'}, status=status.HTTP_404_NOT_FOUND)


class EmployeeEvaluationViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar evaluaciones de empleados"""
    queryset = EmployeeEvaluation.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return EmployeeEvaluationCreateSerializer
        return EmployeeEvaluationSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'employee', 'quarter', 'role', 'supervisor'
        ).prefetch_related('objectives', 'attachments')
        
        # Filtros
        quarter_id = self.request.query_params.get('quarter')
        if quarter_id:
            queryset = queryset.filter(quarter_id=quarter_id)
        
        employee_id = self.request.query_params.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        supervisor_id = self.request.query_params.get('supervisor')
        if supervisor_id:
            queryset = queryset.filter(supervisor_id=supervisor_id)
        
        evaluation_status = self.request.query_params.get('status')
        if evaluation_status:
            queryset = queryset.filter(status=evaluation_status)
        
        return queryset.order_by('-quarter__year', '-quarter__quarter', 'employee__last_name')
    
    @action(detail=True, methods=['post'])
    def send_objectives(self, request, pk=None):
        """Enviar objetivos por email al empleado"""
        evaluation = self.get_object()
        
        # Verificar permisos (solo el supervisor o admin puede enviar)
        if not (request.user == evaluation.supervisor or request.user.is_staff):
            return Response(
                {'detail': 'No tienes permisos para enviar objetivos de esta evaluación'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Renderizar el email
            context = {
                'evaluation': evaluation,
                'employee': evaluation.employee,
                'supervisor': evaluation.supervisor,
                'objectives': evaluation.objectives.all().order_by('objective__category__order', 'objective__title'),
                'quarter': evaluation.quarter,
            }
            
            html_content = render_to_string('evaluation/objectives_email.html', context)
            text_content = render_to_string('evaluation/objectives_email.txt', context)
            
            # Crear el email
            subject = f'Objetivos Trimestrales - {evaluation.quarter}'
            email = EmailMessage(
                subject=subject,
                body=html_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[evaluation.employee.email],
                cc=[evaluation.supervisor.email] if evaluation.supervisor.email != evaluation.employee.email else []
            )
            email.content_subtype = 'html'
            
            # Adjuntar archivos si existen
            for attachment in evaluation.attachments.all():
                if os.path.exists(attachment.file.path):
                    email.attach_file(attachment.file.path)
            
            # Enviar email
            email.send()
            
            # Actualizar la evaluación
            evaluation.objectives_sent_date = timezone.now()
            if evaluation.status == 'ASSIGNED':
                evaluation.status = 'IN_PROGRESS'
            evaluation.save()
            
            return Response({'detail': 'Objetivos enviados correctamente'})
            
        except Exception as e:
            return Response(
                {'detail': f'Error al enviar el email: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def complete_evaluation(self, request, pk=None):
        """Completar la evaluación calculando la puntuación general"""
        evaluation = self.get_object()
        
        # Verificar permisos
        if not (request.user == evaluation.supervisor or request.user.is_staff):
            return Response(
                {'detail': 'No tienes permisos para completar esta evaluación'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar que todos los objetivos estén evaluados
        unevaluated = evaluation.objectives.filter(score__isnull=True)
        if unevaluated.exists():
            return Response(
                {'detail': f'Faltan evaluar {unevaluated.count()} objetivos'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calcular puntuación ponderada
        total_weight = sum(obj.get_effective_weight() for obj in evaluation.objectives.all())
        if total_weight > 0:
            weighted_score = sum(
                obj.score * obj.get_effective_weight() 
                for obj in evaluation.objectives.all() 
                if obj.score is not None
            ) / total_weight
            evaluation.overall_score = round(weighted_score, 2)
        
        # Actualizar estado y fecha
        evaluation.status = 'COMPLETED'
        evaluation.evaluation_completed_date = timezone.now()
        evaluation.evaluation_notes = request.data.get('evaluation_notes', evaluation.evaluation_notes)
        evaluation.save()
        
        serializer = self.get_serializer(evaluation)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Obtener resumen de evaluaciones por trimestre"""
        quarter_id = request.query_params.get('quarter')
        
        if quarter_id:
            quarters = Quarter.objects.filter(id=quarter_id)
        else:
            # Últimos 4 trimestres
            quarters = Quarter.objects.all()[:4]
        
        summaries = []
        for quarter in quarters:
            evaluations = EmployeeEvaluation.objects.filter(quarter=quarter)
            
            # Calcular promedios por categoría
            technical_avg = EvaluationObjective.objects.filter(
                evaluation__quarter=quarter,
                objective__category__name='TECHNICAL',
                score__isnull=False
            ).aggregate(avg=Avg('score'))['avg']
            
            collaboration_avg = EvaluationObjective.objects.filter(
                evaluation__quarter=quarter,
                objective__category__name='COLLABORATION',
                score__isnull=False
            ).aggregate(avg=Avg('score'))['avg']
            
            growth_avg = EvaluationObjective.objects.filter(
                evaluation__quarter=quarter,
                objective__category__name='GROWTH',
                score__isnull=False
            ).aggregate(avg=Avg('score'))['avg']
            
            summary_data = {
                'quarter': quarter,
                'total_evaluations': evaluations.count(),
                'assigned_evaluations': evaluations.filter(status='ASSIGNED').count(),
                'in_progress_evaluations': evaluations.filter(status='IN_PROGRESS').count(),
                'completed_evaluations': evaluations.filter(status='COMPLETED').count(),
                'average_score': evaluations.filter(overall_score__isnull=False).aggregate(
                    avg=Avg('overall_score')
                )['avg'],
                'technical_avg': technical_avg,
                'collaboration_avg': collaboration_avg,
                'growth_avg': growth_avg,
            }
            summaries.append(summary_data)
        
        serializer = EvaluationSummarySerializer(summaries, many=True)
        return Response(serializer.data)


class EvaluationObjectiveViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar objetivos específicos de evaluaciones"""
    queryset = EvaluationObjective.objects.all()
    serializer_class = EvaluationObjectiveSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'evaluation', 'objective', 'objective__category'
        )
        
        evaluation_id = self.request.query_params.get('evaluation')
        if evaluation_id:
            queryset = queryset.filter(evaluation_id=evaluation_id)
        
        return queryset.order_by('objective__category__order', 'objective__title')
    
    def update(self, request, *args, **kwargs):
        """Actualizar objetivo de evaluación y marcar fecha de evaluación"""
        response = super().update(request, *args, **kwargs)
        
        # Si se está actualizando la puntuación, marcar fecha de evaluación
        if 'score' in request.data and response.status_code == 200:
            obj = self.get_object()
            if obj.score is not None and not obj.evaluated_at:
                obj.evaluated_at = timezone.now()
                obj.save()
        
        return response


class EvaluationAttachmentViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar adjuntos de evaluaciones"""
    queryset = EvaluationAttachment.objects.all()
    serializer_class = EvaluationAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        evaluation_id = self.request.query_params.get('evaluation')
        if evaluation_id:
            queryset = queryset.filter(evaluation_id=evaluation_id)
        
        return queryset.order_by('-uploaded_at')
    
    def perform_create(self, serializer):
        """Asignar usuario que sube el archivo y calcular tamaño"""
        file_obj = self.request.FILES['file']
        serializer.save(
            uploaded_by=self.request.user,
            filename=file_obj.name,
            file_size=file_obj.size
        )


# Vistas auxiliares para obtener listas de usuarios
class UsersViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet de solo lectura para usuarios (empleados y supervisores)"""
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def employees(self, request):
        """Obtener lista de empleados desde UserProfile activos"""
        from timehub.models import UserProfile
        
        # Obtener usuarios que tienen perfil de TimehHub activo
        employee_profiles = UserProfile.objects.filter(
            is_active=True,
            user__is_active=True
        ).select_related('user').order_by('user__first_name', 'user__last_name')
        
        employees = [profile.user for profile in employee_profiles]
        serializer = self.get_serializer(employees, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def supervisors(self, request):
        """Obtener lista de supervisores desde UserProfile con permisos de evaluación"""
        from timehub.models import UserProfile
        
        # Usuarios que pueden ser supervisores basado en:
        # 1. Son managers de otros empleados (campo manager en UserProfile)
        # 2. Tienen permisos de evaluación en sus roles
        supervisor_profiles = UserProfile.objects.filter(
            is_active=True,
            user__is_active=True
        ).filter(
            Q(managed_employees__isnull=False) |  # Son managers de otros empleados
            Q(roles__permissions__contains=['manage_evaluations']) |  # Permiso de evaluar
            Q(roles__permissions__contains=['assign_objectives'])     # Permiso de asignar
        ).distinct().select_related('user')
        
        supervisors = [profile.user for profile in supervisor_profiles]
        supervisors.sort(key=lambda u: (u.first_name or '', u.last_name or ''))
        
        serializer = self.get_serializer(supervisors, many=True)
        return Response(serializer.data)