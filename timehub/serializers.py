from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Client, Project, Assignment, Period, PeriodLock, TimeEntry,
    LeaveType, LeaveRequest, PlannedAllocation, Meeting,
    PortfolioSnapshot, PortfolioSnapshotRow, AllocationSnapshot,
    AllocationSnapshotCell, UserProfile, Holiday, AuditLog, Country, Role
)


class CountrySerializer(serializers.ModelSerializer):
    work_days_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Country
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_work_days_display(self, obj):
        return obj.get_work_days_display()


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'is_active']
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': False}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        # Usar email como username si no se proporciona username
        if not validated_data.get('username'):
            validated_data['username'] = validated_data['email']
        
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


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
    user_details = UserSerializer(source='user', read_only=True)
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
    user_details = UserSerializer(source='user', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.username', read_only=True)
    business_days = serializers.SerializerMethodField()
    conflicts = serializers.SerializerMethodField()
    holidays_in_range = serializers.SerializerMethodField()
    current_projects = serializers.SerializerMethodField()
    
    class Meta:
        model = LeaveRequest
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'approved_by', 'approved_at', 'current_approval_level']

    def get_business_days(self, obj):
        """Calcula días laborables en el rango de fechas"""
        from .utils import calculate_vacation_days_needed
        if obj.start_date and obj.end_date and obj.user:
            calendar_days, business_days = calculate_vacation_days_needed(
                obj.start_date, obj.end_date, obj.user.id
            )
            return {
                'calendar_days': calendar_days,
                'business_days': business_days
            }
        return None

    def get_conflicts(self, obj):
        """Verifica conflictos con otras solicitudes"""
        from .utils import check_vacation_conflicts
        if obj.start_date and obj.end_date and obj.user:
            return check_vacation_conflicts(
                obj.start_date, obj.end_date, obj.user.id, obj.id
            )
        return []

    def get_holidays_in_range(self, obj):
        """Obtiene feriados en el rango de fechas"""
        from .utils import get_holidays_in_range
        if obj.start_date and obj.end_date and obj.user:
            try:
                user_profile = UserProfile.objects.get(user=obj.user)
                if user_profile.country:
                    return get_holidays_in_range(
                        obj.start_date, obj.end_date, user_profile.country
                    )
            except UserProfile.DoesNotExist:
                pass
        return []

    def get_current_projects(self, obj):
        """Obtiene proyectos activos del usuario en las fechas solicitadas"""
        if obj.start_date and obj.end_date and obj.user:
            from django.db import models
            # Buscar asignaciones activas que se solapan con las fechas de vacaciones
            assignments = Assignment.objects.filter(
                user=obj.user,
                is_active=True,
                start_date__lte=obj.end_date
            ).filter(
                models.Q(end_date__isnull=True) | models.Q(end_date__gte=obj.start_date)
            ).select_related('project', 'project__client')
            
            projects = []
            for assignment in assignments:
                projects.append({
                    'project_id': assignment.project.id,
                    'project_name': assignment.project.name,
                    'project_code': assignment.project.code,
                    'client_name': assignment.project.client.name,
                    'weekly_hours': assignment.weekly_hours_limit,
                    'assignment_start': assignment.start_date.isoformat() if assignment.start_date else None,
                    'assignment_end': assignment.end_date.isoformat() if assignment.end_date else None
                })
            return projects
        return []

    def validate(self, data):
        from .utils import check_vacation_conflicts, calculate_vacation_days_needed
        
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        user = data.get('user')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin.")
        
        # Validar conflictos solo si tenemos todos los datos necesarios
        if start_date and end_date and user:
            # Excluir la solicitud actual si estamos editando
            exclude_id = self.instance.id if self.instance else None
            conflicts = check_vacation_conflicts(start_date, end_date, user.id, exclude_id)
            
            if conflicts:
                conflict_details = []
                for conflict in conflicts:
                    conflict_details.append(
                        f"{conflict['leave_type']}: {conflict['start_date']} - {conflict['end_date']} "
                        f"({conflict['overlap_days']} días de solapamiento)"
                    )
                raise serializers.ValidationError(
                    f"Conflicto con solicitudes existentes: {'; '.join(conflict_details)}"
                )
            
            # Calcular días requeridos y actualizar automáticamente
            calendar_days, business_days = calculate_vacation_days_needed(start_date, end_date, user.id)
            
            # Usar días laborables para tipos que descuentan del balance
            leave_type = data.get('leave_type')
            if leave_type and leave_type.deducts_from_balance:
                data['days_requested'] = business_days
            else:
                data['days_requested'] = calendar_days
        
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
    user_details = UserSerializer(source='user', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    manager_name = serializers.CharField(source='manager.username', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)
    country_code = serializers.CharField(source='country.code', read_only=True)
    roles = RoleSerializer(many=True, read_only=True)
    role_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Role.objects.all(), 
        source='roles', 
        write_only=True,
        required=False
    )
    total_vacation_days = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'user': {'required': False}  # Hacer que user no sea requerido en el serializer
        }
    
    def get_total_vacation_days(self, obj):
        """Calcula el total de días de vacaciones incluyendo acumulados"""
        base_days = float(obj.leave_balance_days)
        accumulated_days = float(obj.accumulated_vacation_days)
        return base_days + accumulated_days

    def create(self, validated_data):
        roles_data = validated_data.pop('roles', [])
        
        # Verificar que el campo user esté presente para crear
        if 'user' not in validated_data:
            raise serializers.ValidationError('El campo user es requerido para crear un perfil')
        
        user_profile = UserProfile.objects.create(**validated_data)
        if roles_data:
            user_profile.roles.set(roles_data)
        return user_profile

    def update(self, instance, validated_data):
        roles_data = validated_data.pop('roles', None)
        
        # No actualizar el campo user en updates
        validated_data.pop('user', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if roles_data is not None:
            instance.roles.set(roles_data)
        
        return instance


class HolidaySerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    country_code = serializers.CharField(source='country.code', read_only=True)
    
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