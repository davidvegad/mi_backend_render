from django.db import models
from django.contrib.auth.models import User, Group
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from datetime import date, datetime
import uuid
from storages.backends.s3boto3 import S3Boto3Storage

s3_storage = S3Boto3Storage()

class Client(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    country = models.ForeignKey('Country', on_delete=models.SET_NULL, null=True, blank=True, related_name='clients')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['name']


class Project(models.Model):
    PROJECT_TYPE_CHOICES = [
        ('FIXED_PRICE', 'Fixed Price'),
        ('TIME_MATERIAL', 'Time & Material'),
        ('RETAINER', 'Retainer'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    leader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='led_projects')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    progress_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )
    
    # Campos de seguimiento - se llenan al crear el proyecto
    approved_hours = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Horas aprobadas para el proyecto"
    )
    budget = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Presupuesto del proyecto"
    )
    project_type = models.CharField(
        max_length=20, 
        choices=PROJECT_TYPE_CHOICES, 
        null=True, 
        blank=True,
        help_text="Tipo de proyecto"
    )
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_CHOICES, 
        default='MEDIUM',
        help_text="Prioridad del proyecto"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def logged_hours(self):
        """Calcula las horas imputadas (de timesheet) para este proyecto"""
        return self.time_entries.filter(status='APPROVED').aggregate(
            total=models.Sum('hours_decimal')
        )['total'] or Decimal('0.00')
    
    @property
    def hours_percentage(self):
        """Calcula el % de horas imputadas vs horas aprobadas"""
        if not self.approved_hours or self.approved_hours == 0:
            return Decimal('0.00')
        
        logged = self.logged_hours
        percentage = (logged / self.approved_hours) * Decimal('100.00')
        return round(percentage, 2)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['code']


class ProjectFollowUp(models.Model):
    STATUS_CHOICES = [
        ('ON_TRACK', 'En Curso'),
        ('AT_RISK', 'En Riesgo'),
        ('DELAYED', 'Retrasado'),
        ('BLOCKED', 'Bloqueado'),
        ('COMPLETED', 'Completado'),
        ('CANCELLED', 'Cancelado'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='follow_ups')
    follow_up_date = models.DateField(help_text="Fecha de la reunión de seguimiento")
    
    # Estado del proyecto en esta reunión
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ON_TRACK')
    progress_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text="% de avance del proyecto"
    )
    observations = models.TextField(help_text="Observaciones de la reunión")
    
    # Métricas calculadas al momento de la reunión
    logged_hours = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Horas imputadas hasta la fecha"
    )
    hours_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="% de horas utilizadas"
    )
    
    # Proyecciones y planes
    estimated_completion_date = models.DateField(
        null=True, 
        blank=True,
        help_text="Fecha estimada de finalización"
    )
    next_milestones = models.TextField(
        blank=True,
        help_text="Próximos hitos"
    )
    risks = models.TextField(
        blank=True,
        help_text="Riesgos identificados"
    )
    actions_required = models.TextField(
        blank=True,
        help_text="Acciones requeridas"
    )
    
    # Información de la reunión
    attendees = models.TextField(
        blank=True,
        help_text="Asistentes a la reunión"
    )
    meeting_notes = models.TextField(
        blank=True,
        help_text="Notas adicionales de la reunión"
    )
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_follow_ups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project.code} - Seguimiento {self.follow_up_date} ({self.get_status_display()})"

    class Meta:
        ordering = ['-follow_up_date']
        unique_together = ['project', 'follow_up_date']  # Un seguimiento por proyecto por fecha
        indexes = [
            models.Index(fields=['project', 'follow_up_date']),
            models.Index(fields=['status']),
        ]


class Assignment(models.Model):
    ROLE_CHOICES = [
        ('DEVELOPER', 'Developer'),
        ('QA', 'QA Tester'),
        ('ANALYST', 'Business Analyst'),
        ('DESIGNER', 'Designer'),
        ('PM', 'Project Manager'),
        ('TECH_LEAD', 'Tech Lead'),
        ('OTHER', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='assignments')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='DEVELOPER')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    weekly_hours_limit = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.project.code} ({self.role})"

    class Meta:
        unique_together = ['user', 'project', 'start_date']
        ordering = ['-start_date']


class Period(models.Model):
    PERIOD_TYPE_CHOICES = [
        ('WEEK', 'Weekly'),
        ('MONTH', 'Monthly'),
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSING', 'Closing'),
        ('CLOSED', 'Closed'),
    ]

    period_type = models.CharField(max_length=10, choices=PERIOD_TYPE_CHOICES, default='WEEK')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.period_type}: {self.start_date} - {self.end_date} ({self.status})"

    class Meta:
        unique_together = ['period_type', 'start_date']
        ordering = ['-start_date']


class PeriodLock(models.Model):
    SOURCE_CHOICES = [
        ('CLOSURE', 'Period Closure'),
        ('LEAVE', 'Leave Request'),
    ]

    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='locks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        scope = "Global"
        if self.user and self.project:
            scope = f"{self.user.username} - {self.project.code}"
        elif self.user:
            scope = f"User: {self.user.username}"
        elif self.project:
            scope = f"Project: {self.project.code}"
        
        return f"Lock {self.period} - {scope} ({self.source})"

    class Meta:
        ordering = ['-created_at']


class TimeEntry(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_entries')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='time_entries')
    local_date = models.DateField()
    hours_decimal = models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_time_entries'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.project.code} - {self.local_date} ({self.hours_decimal}h)"

    class Meta:
        unique_together = ['user', 'project', 'local_date']
        ordering = ['-local_date', 'user__username']
        indexes = [
            models.Index(fields=['user', 'local_date']),
            models.Index(fields=['project', 'local_date']),
            models.Index(fields=['status']),
        ]


class LeaveType(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    is_paid = models.BooleanField(default=True)
    deducts_from_balance = models.BooleanField(default=True)
    requires_attachment = models.BooleanField(default=False)
    approval_levels = models.PositiveIntegerField(default=1)
    max_days_per_request = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['name']


class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    days_requested = models.PositiveIntegerField()
    reason = models.TextField()
    attachment = models.FileField(upload_to='leave_attachments/', storage=s3_storage, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    current_approval_level = models.PositiveIntegerField(default=0)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_leave_requests'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.leave_type.code} - {self.start_date} to {self.end_date}"

    class Meta:
        ordering = ['-created_at']


class PlannedAllocation(models.Model):
    BOOKING_TYPE_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('TENTATIVE', 'Tentative'),
        ('BUFFER', 'Buffer'),
    ]

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='planned_allocations')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='planned_allocations')
    week_start_date = models.DateField()
    hours_planned = models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    booking_type = models.CharField(max_length=10, choices=BOOKING_TYPE_CHOICES, default='CONFIRMED')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.project.code} - Week {self.week_start_date} ({self.hours_planned}h)"

    class Meta:
        unique_together = ['user', 'project', 'week_start_date']
        ordering = ['-week_start_date', 'user__username']
        indexes = [
            models.Index(fields=['user', 'week_start_date']),
            models.Index(fields=['project', 'week_start_date']),
            models.Index(fields=['status']),
        ]


class Meeting(models.Model):
    TYPE_CHOICES = [
        ('STATUS', 'Portfolio Status'),
        ('ALLOCATION', 'Resource Allocation'),
    ]

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]

    meeting_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    week_start_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    title = models.CharField(max_length=200, blank=True)
    agenda = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    attendees = models.ManyToManyField(User, related_name='attended_meetings', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_meetings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_meeting_type_display()} - Week {self.week_start_date}"

    class Meta:
        unique_together = ['meeting_type', 'week_start_date']
        ordering = ['-week_start_date']


class PortfolioSnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='portfolio_snapshots')
    snapshot_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Portfolio Snapshot - {self.meeting} - {self.snapshot_date}"

    class Meta:
        ordering = ['-snapshot_date']


class PortfolioSnapshotRow(models.Model):
    snapshot = models.ForeignKey(PortfolioSnapshot, on_delete=models.CASCADE, related_name='rows')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    progress_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )
    planned_hours = models.DecimalField(max_digits=6, decimal_places=2)
    actual_hours = models.DecimalField(max_digits=6, decimal_places=2)
    approved_hours = models.DecimalField(max_digits=6, decimal_places=2)
    utilization_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    risk_level = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ], default='LOW')
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.snapshot} - {self.project.code}"

    class Meta:
        unique_together = ['snapshot', 'project']


class AllocationSnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='allocation_snapshots')
    snapshot_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Allocation Snapshot - {self.meeting} - {self.snapshot_date}"

    class Meta:
        ordering = ['-snapshot_date']


class AllocationSnapshotCell(models.Model):
    snapshot = models.ForeignKey(AllocationSnapshot, on_delete=models.CASCADE, related_name='cells')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    hours_planned = models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    booking_type = models.CharField(max_length=10, choices=PlannedAllocation.BOOKING_TYPE_CHOICES)
    capacity_used = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.snapshot} - {self.user.username} - {self.project.code}"

    class Meta:
        unique_together = ['snapshot', 'user', 'project']


class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True)  # ISO 3166-1 alpha-3
    annual_vacation_days = models.PositiveIntegerField(default=30)
    work_days = models.JSONField(default=list)  # [1,2,3,4,5] para lun-vie
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Días máximos por tipo de permiso según leyes del país
    max_maternity_days = models.PositiveIntegerField(default=98, help_text="Días máximos de licencia por maternidad")
    max_paternity_days = models.PositiveIntegerField(default=10, help_text="Días máximos de licencia por paternidad")
    max_sick_days = models.PositiveIntegerField(default=30, help_text="Días máximos por enfermedad")
    max_bereavement_days = models.PositiveIntegerField(default=3, help_text="Días máximos por luto")
    max_personal_days = models.PositiveIntegerField(default=5, help_text="Días máximos de permiso personal")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Countries'

    def get_work_days_display(self):
        """Retorna días laborables en formato legible"""
        days = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        return [days[i-1] for i in self.work_days]


class Role(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    permissions = models.JSONField(default=list, help_text="Lista de permisos del rol")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['name']


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='timehub_profile')
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    weekly_hours = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=Decimal('40.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    accumulated_vacation_days = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Días de vacaciones acumulados de años anteriores"
    )
    manager = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='managed_employees'
    )
    roles = models.ManyToManyField(Role, blank=True, related_name='user_profiles')
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def leave_balance_days(self):
        """Calcula el balance de días de vacaciones disponibles"""
        if not self.country:
            return Decimal('0.00')
        
        # Días anuales según el país
        annual_days = Decimal(str(self.country.annual_vacation_days))
        
        # Días acumulados de años anteriores
        accumulated_days = self.accumulated_vacation_days or Decimal('0.00')
        
        # Días realmente consumidos este año (solo vacaciones que descuentan del balance y ya pasaron)
        current_year = date.today().year
        today = date.today()
        used_days = Decimal('0.00')
        
        # Solo contar solicitudes aprobadas que ya terminaron
        vacation_requests = self.user.leave_requests.filter(
            leave_type__deducts_from_balance=True,
            status='APPROVED',
            start_date__year=current_year,
            end_date__lt=today  # Solo días ya consumidos
        )
        
        for request in vacation_requests:
            used_days += Decimal(str(request.days_requested))
        
        # Balance total = días anuales + acumulados - usados
        total_balance = annual_days + accumulated_days - used_days
        
        return max(total_balance, Decimal('0.00'))
    
    def get_leave_type_balance(self, leave_type_code):
        """Obtiene el balance para un tipo específico de permiso"""
        if not self.country:
            return {'available': 0, 'used': 0, 'max_allowed': 0}
        
        current_year = date.today().year
        
        # Mapeo de códigos de tipo de permiso a campos del país
        type_mapping = {
            'MATERNITY': self.country.max_maternity_days,
            'MAT': self.country.max_maternity_days,  # Compatibilidad con código existente
            'PATERNITY': self.country.max_paternity_days,
            'ENF': self.country.max_sick_days,  # Código existente para enfermedad
            'SICK': self.country.max_sick_days,
            'BEREAVEMENT': self.country.max_bereavement_days,
            'PER': self.country.max_personal_days,  # Código existente para personal
            'PERSONAL': self.country.max_personal_days,
        }
        
        # Días realmente consumidos este año (solicitudes aprobadas que ya pasaron)
        today = date.today()
        used_requests = self.user.leave_requests.filter(
            leave_type__code=leave_type_code,
            status='APPROVED',
            start_date__year=current_year,
            end_date__lt=today  # Solo contar días que ya pasaron
        )
        
        used_days = sum(request.days_requested for request in used_requests)
        
        if leave_type_code in ['VACATION', 'VAC']:
            # Para vacaciones, usar el balance calculado
            available = float(self.leave_balance_days)
            max_allowed = self.country.annual_vacation_days + float(self.accumulated_vacation_days or 0)
        else:
            # Para otros tipos, usar límites del país
            max_allowed = type_mapping.get(leave_type_code, 0)
            available = max(max_allowed - used_days, 0)
        
        return {
            'available': available,
            'used': used_days,
            'max_allowed': max_allowed
        }

    def __str__(self):
        return f"{self.user.username} Profile"

    class Meta:
        ordering = ['user__username']


class Holiday(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='holidays', null=True, blank=True)
    name = models.CharField(max_length=200)
    date = models.DateField()
    is_recurring = models.BooleanField(default=False)  # True para feriados anuales como Navidad
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        country_code = self.country.code if self.country else 'GLOBAL'
        return f"{country_code} - {self.name} - {self.date}"

    class Meta:
        ordering = ['country', 'date']


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('APPROVE', 'Approve'),
        ('REJECT', 'Reject'),
        ('SUBMIT', 'Submit'),
        ('PUBLISH', 'Publish'),
    ]

    entity_type = models.CharField(max_length=50)
    entity_id = models.CharField(max_length=50)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    actor = models.ForeignKey(User, on_delete=models.CASCADE)
    payload = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.actor.username} - {self.action} - {self.entity_type}:{self.entity_id}"

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['actor', 'timestamp']),
        ]
