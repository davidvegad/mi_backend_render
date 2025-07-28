from django.db import models
from django.contrib.auth.models import User, Group
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid


class Client(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['name']


class Project(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['code']


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
    attachment = models.FileField(upload_to='leave_attachments/', null=True, blank=True)
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


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='timehub_profile')
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    weekly_hours = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=Decimal('40.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    leave_balance_days = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    manager = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='managed_employees'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Profile"

    class Meta:
        ordering = ['user__username']


class Holiday(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()
    is_recurring = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.date}"

    class Meta:
        unique_together = ['name', 'date']
        ordering = ['date']


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
