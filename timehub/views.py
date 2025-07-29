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
    Client, Project, Assignment, Period, PeriodLock, TimeEntry,
    LeaveType, LeaveRequest, PlannedAllocation, Meeting,
    PortfolioSnapshot, PortfolioSnapshotRow, AllocationSnapshot,
    AllocationSnapshotCell, UserProfile, Holiday, AuditLog, Country, Role
)
from .serializers import (
    ClientSerializer, ProjectSerializer, AssignmentSerializer,
    PeriodSerializer, PeriodLockSerializer, TimeEntrySerializer,
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
