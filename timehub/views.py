from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.db import transaction, models
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    Client, Project, ProjectFollowUp, Assignment, Period, PeriodLock, TimeEntry,
    LeaveType, LeaveRequest, PlannedAllocation, Meeting,
    PortfolioSnapshot, PortfolioSnapshotRow, AllocationSnapshot,
    AllocationSnapshotCell, UserProfile, Holiday, AuditLog, Country, Role
)
from .serializers import (
    ClientSerializer, ProjectSerializer, ProjectFollowUpSerializer, ProjectSummarySerializer,
    AssignmentSerializer, PeriodSerializer, PeriodLockSerializer, TimeEntrySerializer,
    LeaveTypeSerializer, LeaveRequestSerializer, PlannedAllocationSerializer,
    MeetingSerializer, PortfolioSnapshotSerializer, AllocationSnapshotSerializer,
    UserProfileSerializer, HolidaySerializer, AuditLogSerializer,
    TimeEntrySubmitSerializer, TimeEntryApprovalSerializer,
    LeaveRequestApprovalSerializer, PeriodCloseSerializer, UserSerializer,
    CountrySerializer, RoleSerializer
)


class TimehubTokenObtainPairView(TokenObtainPairView):
    pass


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Client.objects.all()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Project.objects.select_related('client', 'client__country', 'leader')
        is_active = self.request.query_params.get('is_active')
        client_id = self.request.query_params.get('client')
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        if client_id:
            queryset = queryset.filter(client_id=client_id)
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Endpoint para obtener resumen de proyectos con métricas de seguimiento"""
        # Filtros
        is_active = request.query_params.get('is_active')
        leader = request.query_params.get('leader')
        client = request.query_params.get('client')
        priority = request.query_params.get('priority')
        
        # Query base - solo proyectos que requieren seguimiento
        queryset = Project.objects.select_related('client', 'client__country', 'leader').filter(
            requires_follow_up=True
        )
        
        # Aplicar filtros
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        if leader:
            queryset = queryset.filter(leader__username__icontains=leader)
        if client:
            queryset = queryset.filter(client__name__icontains=client)
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Construir datos del resumen
        summary_data = []
        for project in queryset:
            # Obtener último seguimiento
            last_follow_up = project.follow_ups.first()  # Ya ordenado por -follow_up_date
            follow_up_count = project.follow_ups.count()
            
            # Calcular tendencias (comparar últimos dos seguimientos)
            progress_trend = None
            hours_trend = None
            
            if follow_up_count >= 2:
                follow_ups = list(project.follow_ups.all()[:2])
                current_follow_up = follow_ups[0]
                previous_follow_up = follow_ups[1]
                
                # Tendencia de progreso
                progress_diff = current_follow_up.progress_percentage - previous_follow_up.progress_percentage
                if progress_diff > 0:
                    progress_trend = 'IMPROVING'
                elif progress_diff < 0:
                    progress_trend = 'DECLINING'
                else:
                    progress_trend = 'STABLE'
                
                # Tendencia de horas
                hours_diff = current_follow_up.hours_percentage - previous_follow_up.hours_percentage
                if project.approved_hours:
                    if current_follow_up.hours_percentage <= 80:
                        hours_trend = 'UNDER_BUDGET'
                    elif current_follow_up.hours_percentage <= 100:
                        hours_trend = 'ON_BUDGET'
                    else:
                        hours_trend = 'OVER_BUDGET'
            
            # Calcular métricas con manejo de errores
            try:
                logged_hours = float(project.logged_hours)
                hours_percentage = float(project.hours_percentage)
            except Exception as e:
                print(f"Error calculando horas para proyecto {project.id}: {e}")
                logged_hours = 0.0
                hours_percentage = 0.0
            
            # Serializar último seguimiento con manejo de errores
            last_follow_up_data = None
            if last_follow_up:
                try:
                    last_follow_up_data = {
                        'id': last_follow_up.id,
                        'follow_up_date': last_follow_up.follow_up_date,
                        'status': last_follow_up.status,
                        'progress_percentage': float(last_follow_up.progress_percentage),
                        'observations': last_follow_up.observations,
                    }
                except Exception as e:
                    print(f"Error serializando follow-up {last_follow_up.id}: {e}")
                    last_follow_up_data = None
            
            summary_data.append({
                'id': project.id,
                'code': project.code,
                'name': project.name,
                'client_name': project.client.name,
                'client_country': project.client.country.name if project.client.country else None,
                'leader_name': project.leader.username if project.leader else 'Sin asignar',
                'start_date': project.start_date.isoformat() if project.start_date else None,
                'end_date': project.end_date.isoformat() if project.end_date else None,
                'approved_hours': float(project.approved_hours) if project.approved_hours else None,
                'budget': float(project.budget) if project.budget else None,
                'project_type': project.project_type,
                'priority': project.priority,
                'logged_hours': logged_hours,
                'hours_percentage': hours_percentage,
                'is_active': project.is_active,
                'last_follow_up': last_follow_up_data,
                'follow_up_count': follow_up_count,
                'progress_trend': progress_trend,
                'hours_trend': hours_trend,
            })
        
        # Retornar datos directamente para evitar errores de serialización
        return Response(summary_data)
    
    @action(detail=True, methods=['get'])
    def metrics(self, request, pk=None):
        """Endpoint para obtener métricas detalladas de un proyecto"""
        project = self.get_object()
        
        # Calcular métricas adicionales
        total_assignments = project.assignments.filter(is_active=True).count()
        total_time_entries = project.time_entries.count()
        approved_time_entries = project.time_entries.filter(status='APPROVED').count()
        
        # Horas por mes (últimos 12 meses)
        from django.utils import timezone
        from datetime import datetime, timedelta
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=365)
        
        monthly_hours = []
        current_date = start_date.replace(day=1)
        
        while current_date <= end_date:
            next_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
            month_hours = project.time_entries.filter(
                status='APPROVED',
                local_date__gte=current_date,
                local_date__lt=next_month
            ).aggregate(total=models.Sum('hours_decimal'))['total'] or 0
            
            monthly_hours.append({
                'month': current_date.strftime('%Y-%m'),
                'hours': float(month_hours)
            })
            current_date = next_month
        
        return Response({
            'project_id': project.id,
            'project_code': project.code,
            'project_name': project.name,
            'total_assignments': total_assignments,
            'total_time_entries': total_time_entries,
            'approved_time_entries': approved_time_entries,
            'logged_hours': float(project.logged_hours),
            'hours_percentage': float(project.hours_percentage),
            'approved_hours': float(project.approved_hours) if project.approved_hours else 0,
            'budget': float(project.budget) if project.budget else 0,
            'monthly_hours': monthly_hours,
        })


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Assignment.objects.select_related('user', 'project', 'project__client')
        user_id = self.request.query_params.get('user')
        project_id = self.request.query_params.get('project')
        is_active = self.request.query_params.get('is_active')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        return queryset


class PeriodViewSet(viewsets.ModelViewSet):
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        period = self.get_object()
        serializer = PeriodCloseSerializer(data=request.data)
        
        if serializer.is_valid():
            action = serializer.validated_data['action']
            reason = serializer.validated_data.get('reason', '')
            
            if action == 'close':
                period.status = 'CLOSED'
                period.save()
                
                # Crear audit log
                AuditLog.objects.create(
                    entity_type='Period',
                    entity_id=str(period.id),
                    action='CLOSE',
                    actor=request.user,
                    payload={'reason': reason}
                )
                
                return Response({'message': 'Period closed successfully'})
            
            elif action == 'reopen':
                period.status = 'OPEN'
                period.save()
                
                AuditLog.objects.create(
                    entity_type='Period',
                    entity_id=str(period.id),
                    action='REOPEN',
                    actor=request.user,
                    payload={'reason': reason}
                )
                
                return Response({'message': 'Period reopened successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TimeEntryViewSet(viewsets.ModelViewSet):
    queryset = TimeEntry.objects.all()
    serializer_class = TimeEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = TimeEntry.objects.select_related('user', 'project', 'approved_by')
        user_id = self.request.query_params.get('user')
        project_id = self.request.query_params.get('project')
        status_filter = self.request.query_params.get('status')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if date_from:
            queryset = queryset.filter(local_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(local_date__lte=date_to)
            
        return queryset
    
    @action(detail=False, methods=['post'])
    def submit(self, request):
        serializer = TimeEntrySubmitSerializer(data=request.data)
        
        if serializer.is_valid():
            time_entry_ids = serializer.validated_data['time_entry_ids']
            
            with transaction.atomic():
                time_entries = TimeEntry.objects.filter(
                    id__in=time_entry_ids,
                    status__in=['DRAFT', 'REJECTED']  # Permitir re-envío de entradas rechazadas
                )
                
                updated_count = time_entries.update(status='SUBMITTED')
                
                for entry in time_entries:
                    AuditLog.objects.create(
                        entity_type='TimeEntry',
                        entity_id=str(entry.id),
                        action='SUBMIT',
                        actor=request.user
                    )
            
            return Response({
                'message': f'{updated_count} time entries submitted successfully'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        time_entry = self.get_object()
        serializer = TimeEntryApprovalSerializer(data=request.data)
        
        if serializer.is_valid():
            action = serializer.validated_data['action']
            
            if action == 'approve':
                time_entry.status = 'APPROVED'
                time_entry.approved_by = request.user
                time_entry.approved_at = timezone.now()
                time_entry.save()
                
                AuditLog.objects.create(
                    entity_type='TimeEntry',
                    entity_id=str(time_entry.id),
                    action='APPROVE',
                    actor=request.user
                )
                
                return Response({'message': 'Time entry approved successfully'})
            
            elif action == 'reject':
                rejection_reason = serializer.validated_data.get('rejection_reason', '')
                time_entry.status = 'REJECTED'
                time_entry.rejection_reason = rejection_reason
                time_entry.save()
                
                AuditLog.objects.create(
                    entity_type='TimeEntry',
                    entity_id=str(time_entry.id),
                    action='REJECT',
                    actor=request.user,
                    payload={'rejection_reason': rejection_reason}
                )
                
                return Response({'message': 'Time entry rejected successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def bulk_approve(self, request):
        """Bulk approve/reject timesheet entries for a user and week"""
        user_id = request.data.get('user_id')
        week_start = request.data.get('week_start')
        action = request.data.get('action')
        rejection_reason = request.data.get('rejection_reason', '')
        
        if not user_id or not week_start or not action:
            return Response(
                {'error': 'user_id, week_start, and action are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if action not in ['approve', 'reject']:
            return Response(
                {'error': 'action must be either "approve" or "reject"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate week end date
        try:
            from datetime import datetime, timedelta
            week_start_date = datetime.strptime(week_start, '%Y-%m-%d').date()
            week_end_date = week_start_date + timedelta(days=6)
        except ValueError:
            return Response(
                {'error': 'Invalid week_start format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Get all submitted timesheet entries for the user and week
            time_entries = TimeEntry.objects.filter(
                user_id=user_id,
                local_date__gte=week_start_date,
                local_date__lte=week_end_date,
                status='SUBMITTED'
            )
            
            if not time_entries.exists():
                return Response(
                    {'error': 'No submitted time entries found for the specified user and week'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            updated_count = 0
            
            for entry in time_entries:
                if action == 'approve':
                    entry.status = 'APPROVED'
                    entry.approved_by = request.user
                    entry.approved_at = timezone.now()
                    entry.save()
                    
                    AuditLog.objects.create(
                        entity_type='TimeEntry',
                        entity_id=str(entry.id),
                        action='BULK_APPROVE',
                        actor=request.user,
                        payload={'week_start': week_start}
                    )
                    
                elif action == 'reject':
                    entry.status = 'REJECTED'
                    entry.rejection_reason = rejection_reason
                    entry.save()
                    
                    AuditLog.objects.create(
                        entity_type='TimeEntry',
                        entity_id=str(entry.id),
                        action='BULK_REJECT',
                        actor=request.user,
                        payload={'rejection_reason': rejection_reason, 'week_start': week_start}
                    )
                
                updated_count += 1
            
            message = f'Successfully {action}ed {updated_count} time entries for week {week_start}'
            return Response({'message': message, 'updated_count': updated_count})


class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = LeaveType.objects.all()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]
    
    def get_queryset(self):
        queryset = LeaveRequest.objects.select_related('user', 'leave_type', 'approved_by')
        user_id = self.request.query_params.get('user')
        status_filter = self.request.query_params.get('status')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        leave_request = self.get_object()
        
        if leave_request.status == 'DRAFT':
            leave_request.status = 'SUBMITTED'
            leave_request.save()
            
            AuditLog.objects.create(
                entity_type='LeaveRequest',
                entity_id=str(leave_request.id),
                action='SUBMIT',
                actor=request.user
            )
            
            return Response({'message': 'Leave request submitted successfully'})
        
        return Response(
            {'error': 'Leave request cannot be submitted'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave_request = self.get_object()
        serializer = LeaveRequestApprovalSerializer(data=request.data)
        
        if serializer.is_valid():
            action = serializer.validated_data['action']
            
            if action == 'approve':
                leave_request.status = 'APPROVED'
                leave_request.approved_by = request.user
                leave_request.approved_at = timezone.now()
                leave_request.save()
                
                # Crear bloqueos de periodo por leave
                # TODO: Implementar lógica de creación de PeriodLock
                
                AuditLog.objects.create(
                    entity_type='LeaveRequest',
                    entity_id=str(leave_request.id),
                    action='APPROVE',
                    actor=request.user
                )
                
                return Response({'message': 'Leave request approved successfully'})
            
            elif action == 'reject':
                rejection_reason = serializer.validated_data.get('rejection_reason', '')
                leave_request.status = 'REJECTED'
                leave_request.rejection_reason = rejection_reason
                leave_request.save()
                
                AuditLog.objects.create(
                    entity_type='LeaveRequest',
                    entity_id=str(leave_request.id),
                    action='REJECT',
                    actor=request.user,
                    payload={'rejection_reason': rejection_reason}
                )
                
                return Response({'message': 'Leave request rejected successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlannedAllocationViewSet(viewsets.ModelViewSet):
    queryset = PlannedAllocation.objects.all()
    serializer_class = PlannedAllocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = PlannedAllocation.objects.select_related('user', 'project')
        user_id = self.request.query_params.get('user')
        project_id = self.request.query_params.get('project')
        week_start = self.request.query_params.get('week_start')
        status_filter = self.request.query_params.get('status')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if week_start:
            queryset = queryset.filter(week_start_date=week_start)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset
    
    @action(detail=False, methods=['post'])
    def publish(self, request):
        week_start = request.data.get('week_start_date')
        
        if not week_start:
            return Response(
                {'error': 'week_start_date is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            allocations = PlannedAllocation.objects.filter(
                week_start_date=week_start,
                status='DRAFT'
            )
            
            updated_count = allocations.update(status='PUBLISHED')
            
            AuditLog.objects.create(
                entity_type='PlannedAllocation',
                entity_id=f'week_{week_start}',
                action='PUBLISH',
                actor=request.user,
                payload={'week_start_date': week_start}
            )
        
        return Response({
            'message': f'{updated_count} allocations published for week {week_start}'
        })


class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Meeting.objects.select_related('created_by').prefetch_related('attendees')
        meeting_type = self.request.query_params.get('type')
        week_start = self.request.query_params.get('week_start')
        
        if meeting_type:
            queryset = queryset.filter(meeting_type=meeting_type)
        if week_start:
            queryset = queryset.filter(week_start_date=week_start)
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def freeze(self, request, pk=None):
        meeting = self.get_object()
        
        if meeting.meeting_type == 'STATUS':
            # Crear Portfolio Snapshot
            snapshot = PortfolioSnapshot.objects.create(
                meeting=meeting,
                created_by=request.user
            )
            
            # TODO: Crear rows del snapshot con datos actuales
            
            return Response({
                'message': 'Portfolio snapshot created successfully',
                'snapshot_id': snapshot.id
            })
        
        elif meeting.meeting_type == 'ALLOCATION':
            # Crear Allocation Snapshot
            snapshot = AllocationSnapshot.objects.create(
                meeting=meeting,
                created_by=request.user
            )
            
            # TODO: Crear cells del snapshot con datos actuales
            
            return Response({
                'message': 'Allocation snapshot created successfully',
                'snapshot_id': snapshot.id
            })
        
        return Response(
            {'error': 'Invalid meeting type for snapshot'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = UserProfile.objects.select_related('user', 'manager')
        department = self.request.query_params.get('department')
        is_active = self.request.query_params.get('is_active')
        
        if department:
            queryset = queryset.filter(department=department)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        return queryset


class HolidayViewSet(viewsets.ModelViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Holiday.objects.all()
        year = self.request.query_params.get('year')
        is_active = self.request.query_params.get('is_active')
        
        if year:
            queryset = queryset.filter(date__year=year)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        return queryset


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = AuditLog.objects.select_related('actor')
        entity_type = self.request.query_params.get('entity_type')
        entity_id = self.request.query_params.get('entity_id')
        action = self.request.query_params.get('action')
        actor_id = self.request.query_params.get('actor')
        
        if entity_type:
            queryset = queryset.filter(entity_type=entity_type)
        if entity_id:
            queryset = queryset.filter(entity_id=entity_id)
        if action:
            queryset = queryset.filter(action=action)
        if actor_id:
            queryset = queryset.filter(actor_id=actor_id)
            
        return queryset


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = User.objects.all()
        is_active = self.request.query_params.get('is_active')
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        return queryset


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Country.objects.all()
        is_active = self.request.GET.get('is_active')
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        return queryset


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Role.objects.all()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset


class LeaveBalanceViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """Get leave balance for user and year"""
        user_id = request.GET.get('user')
        year = int(request.GET.get('year', datetime.now().year))
        
        if not user_id:
            user_id = request.user.id
            
        balances = []
        
        try:
            user_profile = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=400)
        
        # Get all active leave types to show comprehensive balance
        leave_types = LeaveType.objects.filter(is_active=True)
        
        for leave_type in leave_types:
            # Use the new get_leave_type_balance method
            balance_info = user_profile.get_leave_type_balance(leave_type.code)
            
            # Calculate pending days (submitted requests)
            pending_days = LeaveRequest.objects.filter(
                user_id=user_id,
                leave_type=leave_type,
                status='SUBMITTED',
                start_date__year=year
            ).aggregate(total=models.Sum('days_requested'))['total'] or 0
            
            # Calculate approved pending days (approved but not yet taken)
            from django.utils import timezone
            today = timezone.now().date()
            
            approved_pending_days = LeaveRequest.objects.filter(
                user_id=user_id,
                leave_type=leave_type,
                status='APPROVED',
                start_date__year=year,
                start_date__gt=today
            ).aggregate(total=models.Sum('days_requested'))['total'] or 0
            
            # Calculate available days based on leave type
            if leave_type.deducts_from_balance:
                # For vacation types that deduct from balance
                available_days = balance_info['available'] - pending_days - approved_pending_days
            else:
                # For other types, check if they have country limits
                if balance_info['max_allowed'] > 0:
                    available_days = balance_info['available'] - pending_days - approved_pending_days
                else:
                    # Unlimited types
                    available_days = -1
            
            balances.append({
                'user': user_id,
                'leave_type': leave_type.id,
                'leave_type_name': leave_type.name,
                'annual_entitlement': balance_info['max_allowed'],
                'used_days': balance_info['used'],
                'pending_days': pending_days,
                'approved_pending_days': approved_pending_days,
                'available_days': available_days if available_days == -1 else max(0, available_days),
                'year': year
            })
        
        return Response(balances)


class LeaveCalendarViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """Get leave calendar data for user and year with holidays and non-working days"""
        user_id = request.GET.get('user')
        year = int(request.GET.get('year', datetime.now().year))
        month = request.GET.get('month')  # Optional month filter
        
        if not user_id:
            user_id = request.user.id
            
        try:
            user_profile = UserProfile.objects.get(user_id=user_id)
            country = user_profile.country
        except UserProfile.DoesNotExist:
            country = None
            
        # Get all leave requests for the year
        leave_requests = LeaveRequest.objects.filter(
            user_id=user_id,
            start_date__year__lte=year,
            end_date__year__gte=year
        ).select_related('leave_type')
        
        calendar_days = []
        
        # Create a set of leave request dates for faster lookup
        leave_dates = {}
        for request in leave_requests:
            start_date = max(request.start_date, datetime(year, 1, 1).date())
            end_date = min(request.end_date, datetime(year, 12, 31).date())
            
            current_date = start_date
            while current_date <= end_date:
                status = 'available'
                if request.status == 'APPROVED':
                    if current_date < datetime.now().date():
                        status = 'consumed'
                    else:
                        status = 'approved_pending'
                elif request.status == 'SUBMITTED':
                    status = 'pending'
                
                leave_dates[current_date.isoformat()] = {
                    'status': status,
                    'leave_request_id': request.id,
                    'leave_type': request.leave_type.name
                }
                
                current_date += timedelta(days=1)
        
        # Get holidays for the year/month
        holidays_query = Holiday.objects.filter(
            date__year=year,
            is_active=True
        )
        
        if country:
            holidays_query = holidays_query.filter(country=country)
        
        if month:
            holidays_query = holidays_query.filter(date__month=int(month))
            
        holidays = {holiday.date.isoformat(): holiday.name for holiday in holidays_query}
        
        # Determine date range to process
        if month:
            start_range = datetime(year, int(month), 1).date()
            end_range = datetime(year, int(month) + 1, 1).date() - timedelta(days=1)
        else:
            start_range = datetime(year, 1, 1).date()
            end_range = datetime(year, 12, 31).date()
        
        # Generate calendar data for the entire range
        current_date = start_range
        while current_date <= end_range:
            date_str = current_date.isoformat()
            
            # Determine day type
            day_type = 'working'
            is_weekend = False
            is_holiday = False
            
            if country and country.work_days:
                # weekday() returns 0=Monday, 6=Sunday; we need 1=Monday, 7=Sunday
                day_of_week = current_date.weekday() + 1
                if day_of_week not in country.work_days:
                    day_type = 'non_working'
                    is_weekend = True
            else:
                # Default: weekends are Saturday (5) and Sunday (6) in weekday()
                if current_date.weekday() in [5, 6]:
                    day_type = 'non_working'
                    is_weekend = True
            
            if date_str in holidays:
                day_type = 'holiday'
                is_holiday = True
            
            # Check if there's a leave request for this date
            leave_info = leave_dates.get(date_str)
            
            calendar_entry = {
                'date': date_str,
                'day_type': day_type,
                'is_weekend': is_weekend,
                'is_holiday': is_holiday,
                'holiday_name': holidays.get(date_str),
            }
            
            if leave_info:
                calendar_entry.update({
                    'status': leave_info['status'],
                    'leave_request_id': leave_info['leave_request_id'],
                    'leave_type': leave_info['leave_type']
                })
            else:
                calendar_entry['status'] = 'available'
            
            calendar_days.append(calendar_entry)
            current_date += timedelta(days=1)
        
        return Response(calendar_days)


class ProjectAssignmentViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """Get project assignments for user in date range"""
        user_id = request.GET.get('user')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if not user_id:
            user_id = request.user.id
            
        if not start_date or not end_date:
            return Response({'error': 'start_date and end_date are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Get assignments that overlap with the requested date range
        assignments = Assignment.objects.filter(
            user_id=user_id,
            is_active=True,
            start_date__lte=end_date
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=start_date)
        ).select_related('project', 'project__client', 'project__leader')
        
        project_assignments = []
        
        for assignment in assignments:
            # Calculate overlap days
            overlap_start = max(start_date, assignment.start_date)
            overlap_end = min(end_date, assignment.end_date or datetime(2099, 12, 31).date())
            overlap_days = (overlap_end - overlap_start).days + 1 if overlap_start <= overlap_end else 0
            
            if overlap_days > 0:
                # Get planned allocations for better hour estimates
                weekly_allocation = 0
                total_planned_hours = 0
                
                allocations = PlannedAllocation.objects.filter(
                    user_id=user_id,
                    project=assignment.project,
                    week_start_date__range=[
                        start_date - timedelta(days=start_date.weekday()),
                        end_date
                    ]
                ).aggregate(
                    avg_hours=models.Avg('hours_planned'),
                    total_hours=models.Sum('hours_planned')
                )
                
                weekly_allocation = float(allocations['avg_hours'] or assignment.weekly_hours_limit or 20)
                total_planned_hours = float(allocations['total_hours'] or 0)
                
                project_assignments.append({
                    'project_id': assignment.project.id,
                    'project_code': assignment.project.code,
                    'project_name': assignment.project.name,
                    'project_leader': assignment.project.leader.get_full_name() if assignment.project.leader else 'Sin asignar',
                    'client_name': assignment.project.client.name,
                    'start_date': assignment.start_date.isoformat(),
                    'end_date': assignment.end_date.isoformat() if assignment.end_date else None,
                    'overlap_days': overlap_days,
                    'weekly_allocation': weekly_allocation,
                    'total_planned_hours': total_planned_hours
                })
        
        return Response(project_assignments)


class ProjectFollowUpViewSet(viewsets.ModelViewSet):
    queryset = ProjectFollowUp.objects.all()
    serializer_class = ProjectFollowUpSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ProjectFollowUp.objects.select_related('project', 'created_by')
        project_id = self.request.query_params.get('project')
        status_filter = self.request.query_params.get('status')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if date_from:
            queryset = queryset.filter(follow_up_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(follow_up_date__lte=date_to)
            
        return queryset
    
    def perform_create(self, serializer):
        # Auto-calcular métricas del proyecto al momento de crear el seguimiento
        project = serializer.validated_data['project']
        logged_hours = project.logged_hours
        hours_percentage = project.hours_percentage
        
        serializer.save(
            created_by=self.request.user,
            logged_hours=logged_hours,
            hours_percentage=hours_percentage
        )
    
    @action(detail=False, methods=['get'], url_path='by-project/(?P<project_id>[^/.]+)')
    def by_project(self, request, project_id=None):
        """Obtener todos los seguimientos de un proyecto específico"""
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'Proyecto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        follow_ups = ProjectFollowUp.objects.filter(project=project).select_related('created_by')
        serializer = self.get_serializer(follow_ups, many=True)
        return Response(serializer.data)
