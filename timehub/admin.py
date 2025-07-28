from django.contrib import admin
from .models import (
    Client, Project, Assignment, Period, PeriodLock, TimeEntry,
    LeaveType, LeaveRequest, PlannedAllocation, Meeting,
    PortfolioSnapshot, PortfolioSnapshotRow, AllocationSnapshot,
    AllocationSnapshotCell, UserProfile, Holiday, AuditLog
)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['code', 'name']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'client', 'leader', 'progress_percentage', 'is_active']
    list_filter = ['is_active', 'client', 'start_date']
    search_fields = ['code', 'name', 'client__name']
    raw_id_fields = ['leader']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'role', 'start_date', 'end_date', 'is_active']
    list_filter = ['role', 'is_active', 'start_date']
    search_fields = ['user__username', 'project__code']
    raw_id_fields = ['user', 'project']


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ['period_type', 'start_date', 'end_date', 'status']
    list_filter = ['period_type', 'status']
    ordering = ['-start_date']


@admin.register(PeriodLock)
class PeriodLockAdmin(admin.ModelAdmin):
    list_display = ['period', 'user', 'project', 'source', 'created_at']
    list_filter = ['source', 'created_at']
    raw_id_fields = ['user', 'project']


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'local_date', 'hours_decimal', 'status']
    list_filter = ['status', 'local_date', 'project']
    search_fields = ['user__username', 'project__code']
    raw_id_fields = ['user', 'project', 'approved_by']
    ordering = ['-local_date']


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_paid', 'deducts_from_balance', 'is_active']
    list_filter = ['is_paid', 'deducts_from_balance', 'is_active']


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'leave_type', 'start_date', 'end_date', 'days_requested', 'status']
    list_filter = ['status', 'leave_type', 'start_date']
    search_fields = ['user__username']
    raw_id_fields = ['user', 'approved_by']
    ordering = ['-created_at']


@admin.register(PlannedAllocation)
class PlannedAllocationAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'week_start_date', 'hours_planned', 'booking_type', 'status']
    list_filter = ['booking_type', 'status', 'week_start_date']
    search_fields = ['user__username', 'project__code']
    raw_id_fields = ['user', 'project']
    ordering = ['-week_start_date']


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['meeting_type', 'week_start_date', 'status', 'created_by']
    list_filter = ['meeting_type', 'status', 'week_start_date']
    raw_id_fields = ['created_by', 'attendees']
    ordering = ['-week_start_date']


@admin.register(PortfolioSnapshot)
class PortfolioSnapshotAdmin(admin.ModelAdmin):
    list_display = ['meeting', 'snapshot_date', 'created_by']
    list_filter = ['snapshot_date']
    raw_id_fields = ['created_by']
    ordering = ['-snapshot_date']


@admin.register(AllocationSnapshot)
class AllocationSnapshotAdmin(admin.ModelAdmin):
    list_display = ['meeting', 'snapshot_date', 'created_by']
    list_filter = ['snapshot_date']
    raw_id_fields = ['created_by']
    ordering = ['-snapshot_date']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'department', 'position', 'weekly_hours', 'is_active']
    list_filter = ['department', 'is_active', 'hire_date']
    search_fields = ['user__username', 'employee_id']
    raw_id_fields = ['user', 'manager']


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'is_recurring', 'is_active']
    list_filter = ['is_recurring', 'is_active', 'date']
    ordering = ['date']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['actor', 'action', 'entity_type', 'entity_id', 'timestamp']
    list_filter = ['action', 'entity_type', 'timestamp']
    search_fields = ['actor__username', 'entity_type', 'entity_id']
    raw_id_fields = ['actor']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']
