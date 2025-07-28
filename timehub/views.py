from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    Client, Project, Assignment, Period, PeriodLock, TimeEntry,
    LeaveType, LeaveRequest, PlannedAllocation, Meeting,
    PortfolioSnapshot, PortfolioSnapshotRow, AllocationSnapshot,
    AllocationSnapshotCell, UserProfile, Holiday, AuditLog
)
from .serializers import (
    ClientSerializer, ProjectSerializer, AssignmentSerializer,
    PeriodSerializer, PeriodLockSerializer, TimeEntrySerializer,
    LeaveTypeSerializer, LeaveRequestSerializer, PlannedAllocationSerializer,
    MeetingSerializer, PortfolioSnapshotSerializer, AllocationSnapshotSerializer,
    UserProfileSerializer, HolidaySerializer, AuditLogSerializer,
    TimeEntrySubmitSerializer, TimeEntryApprovalSerializer,
    LeaveRequestApprovalSerializer, PeriodCloseSerializer, UserSerializer
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
        queryset = Project.objects.select_related('client', 'leader')
        is_active = self.request.query_params.get('is_active')
        client_id = self.request.query_params.get('client')
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        if client_id:
            queryset = queryset.filter(client_id=client_id)
            
        return queryset


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


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = User.objects.all()
        is_active = self.request.query_params.get('is_active')
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        return queryset
