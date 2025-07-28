from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Client, Project, Assignment, Period, PeriodLock, TimeEntry,
    LeaveType, LeaveRequest, PlannedAllocation, Meeting,
    PortfolioSnapshot, PortfolioSnapshotRow, AllocationSnapshot,
    AllocationSnapshotCell, UserProfile, Holiday, AuditLog
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ProjectSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    leader_name = serializers.CharField(source='leader.username', read_only=True)
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class AssignmentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    project_code = serializers.CharField(source='project.code', read_only=True)
    project_client_name = serializers.CharField(source='project.client.name', read_only=True)
    
    class Meta:
        model = Assignment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class PeriodLockSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    period_display = serializers.CharField(source='period.__str__', read_only=True)
    
    class Meta:
        model = PeriodLock
        fields = '__all__'
        read_only_fields = ['created_at']


class TimeEntrySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    project_code = serializers.CharField(source='project.code', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.username', read_only=True)
    
    class Meta:
        model = TimeEntry
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'approved_by', 'approved_at']

    def validate(self, data):
        from django.db import models
        user = data.get('user')
        project = data.get('project')
        local_date = data.get('local_date')
        
        # Validar que existe asignación vigente (temporalmente deshabilitado para pruebas)
        # if user and project and local_date:
        #     assignment_exists = Assignment.objects.filter(
        #         user=user,
        #         project=project,
        #         start_date__lte=local_date,
        #         is_active=True
        #     ).filter(
        #         models.Q(end_date__isnull=True) | models.Q(end_date__gte=local_date)
        #     ).exists()
        #     
        #     if not assignment_exists:
        #         raise serializers.ValidationError(
        #             "No existe una asignación vigente para este usuario y proyecto en la fecha especificada."
        #         )
        
        return data


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class LeaveRequestSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.username', read_only=True)
    
    class Meta:
        model = LeaveRequest
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'approved_by', 'approved_at', 'current_approval_level']

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin.")
        
        return data


class PlannedAllocationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    project_code = serializers.CharField(source='project.code', read_only=True)
    
    class Meta:
        model = PlannedAllocation
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class MeetingSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    attendees_names = serializers.StringRelatedField(source='attendees', many=True, read_only=True)
    
    class Meta:
        model = Meeting
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class PortfolioSnapshotRowSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    project_code = serializers.CharField(source='project.code', read_only=True)
    
    class Meta:
        model = PortfolioSnapshotRow
        fields = '__all__'


class PortfolioSnapshotSerializer(serializers.ModelSerializer):
    rows = PortfolioSnapshotRowSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    meeting_display = serializers.CharField(source='meeting.__str__', read_only=True)
    
    class Meta:
        model = PortfolioSnapshot
        fields = '__all__'
        read_only_fields = ['snapshot_date']


class AllocationSnapshotCellSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    project_code = serializers.CharField(source='project.code', read_only=True)
    
    class Meta:
        model = AllocationSnapshotCell
        fields = '__all__'


class AllocationSnapshotSerializer(serializers.ModelSerializer):
    cells = AllocationSnapshotCellSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    meeting_display = serializers.CharField(source='meeting.__str__', read_only=True)
    
    class Meta:
        model = AllocationSnapshot
        fields = '__all__'
        read_only_fields = ['snapshot_date']


class UserProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    manager_name = serializers.CharField(source='manager.username', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class AuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.username', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ['timestamp']


# Serializers para acciones especiales
class TimeEntrySubmitSerializer(serializers.Serializer):
    time_entry_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )


class TimeEntryApprovalSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)


class LeaveRequestApprovalSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)


class PeriodCloseSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['close', 'reopen'])
    reason = serializers.CharField(required=False, allow_blank=True)