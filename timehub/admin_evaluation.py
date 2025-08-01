# Admin para el sistema de evaluación trimestral
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models_evaluation import (
    EvaluationRole, ObjectiveCategory, Objective, Quarter, 
    EmployeeEvaluation, EvaluationObjective, EvaluationAttachment
)


@admin.register(EvaluationRole)
class EvaluationRoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'objectives_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def objectives_count(self, obj):
        count = obj.objective_set.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:timehub_objective_changelist') + f'?role__id__exact={obj.id}'
            return format_html('<a href="{}">{} objetivos</a>', url, count)
        return '0 objetivos'
    objectives_count.short_description = 'Objetivos'


@admin.register(ObjectiveCategory)
class ObjectiveCategoryAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'order', 'objectives_count']
    list_editable = ['order']
    ordering = ['order']
    
    def objectives_count(self, obj):
        count = obj.objective_set.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:timehub_objective_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}">{} objetivos</a>', url, count)
        return '0 objetivos'
    objectives_count.short_description = 'Objetivos'


@admin.register(Objective)
class ObjectiveAdmin(admin.ModelAdmin):
    list_display = ['title', 'role', 'category', 'weight', 'is_active', 'created_at']
    list_filter = ['role', 'category', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'role__name']
    ordering = ['role', 'category__order', 'title']
    list_editable = ['weight', 'is_active']
    
    fieldsets = (
        (None, {
            'fields': ('role', 'category', 'title', 'description')
        }),
        ('Configuración', {
            'fields': ('weight', 'is_active')
        }),
    )


@admin.register(Quarter)
class QuarterAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'start_date', 'end_date', 'is_active', 'evaluations_count']
    list_filter = ['year', 'quarter', 'is_active']
    ordering = ['-year', '-quarter']
    list_editable = ['is_active']
    
    def evaluations_count(self, obj):
        count = obj.employeeevaluation_set.count()
        if count > 0:
            url = reverse('admin:timehub_employeeevaluation_changelist') + f'?quarter__id__exact={obj.id}'
            return format_html('<a href="{}">{} evaluaciones</a>', url, count)
        return '0 evaluaciones'
    evaluations_count.short_description = 'Evaluaciones'


class EvaluationObjectiveInline(admin.TabularInline):
    model = EvaluationObjective
    extra = 0
    readonly_fields = ['objective', 'get_effective_weight']
    fields = ['objective', 'custom_description', 'custom_weight', 'get_effective_weight', 'score', 'evaluator_comments']
    
    def get_effective_weight(self, obj):
        if obj.id:
            return obj.get_effective_weight()
        return '-'
    get_effective_weight.short_description = 'Peso Efectivo'


class EvaluationAttachmentInline(admin.TabularInline):
    model = EvaluationAttachment
    extra = 0
    readonly_fields = ['uploaded_by', 'uploaded_at', 'file_size']
    fields = ['file', 'filename', 'uploaded_by', 'uploaded_at']


@admin.register(EmployeeEvaluation)
class EmployeeEvaluationAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'quarter', 'role', 'supervisor', 'status', 
        'overall_score', 'objectives_sent_date', 'evaluation_completed_date'
    ]
    list_filter = ['status', 'quarter', 'role', 'assigned_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'supervisor__first_name', 'supervisor__last_name']
    ordering = ['-quarter__year', '-quarter__quarter', 'employee__last_name']
    readonly_fields = ['assigned_date', 'overall_score', 'completion_progress']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('employee', 'quarter', 'role', 'supervisor')
        }),
        ('Estado', {
            'fields': ('status', 'assigned_date', 'objectives_sent_date', 'evaluation_completed_date')
        }),
        ('Evaluación', {
            'fields': ('overall_score', 'completion_progress')
        }),
        ('Notas', {
            'fields': ('assignment_notes', 'evaluation_notes'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [EvaluationObjectiveInline, EvaluationAttachmentInline]
    
    def completion_progress(self, obj):
        total = obj.objectives.count()
        if total == 0:
            return 'Sin objetivos'
        
        evaluated = obj.objectives.filter(score__isnull=False).count()
        percentage = (evaluated / total) * 100
        
        color = 'red' if percentage < 50 else 'orange' if percentage < 100 else 'green'
        return format_html(
            '<span style="color: {};">{}/{} objetivos ({}%)</span>',
            color, evaluated, total, round(percentage, 1)
        )
    completion_progress.short_description = 'Progreso de Evaluación'
    
    actions = ['send_objectives', 'complete_evaluation']
    
    def send_objectives(self, request, queryset):
        """Acción para enviar objetivos por email"""
        sent_count = 0
        for evaluation in queryset:
            if evaluation.status == 'ASSIGNED':
                # Aquí iría la lógica de envío de email
                # Por ahora solo actualizamos el estado
                evaluation.status = 'IN_PROGRESS'
                evaluation.objectives_sent_date = timezone.now()
                evaluation.save()
                sent_count += 1
        
        self.message_user(request, f'Se enviaron objetivos para {sent_count} evaluaciones.')
    send_objectives.short_description = 'Enviar objetivos por email'
    
    def complete_evaluation(self, request, queryset):
        """Acción para completar evaluaciones"""
        completed_count = 0
        for evaluation in queryset:
            if evaluation.status in ['IN_PROGRESS', 'PENDING_REVIEW']:
                # Verificar que todos los objetivos estén evaluados
                unevaluated = evaluation.objectives.filter(score__isnull=True).count()
                if unevaluated == 0:
                    # Calcular puntuación general
                    objectives = evaluation.objectives.all()
                    if objectives:
                        total_weight = sum(obj.get_effective_weight() for obj in objectives)
                        if total_weight > 0:
                            weighted_score = sum(
                                obj.score * obj.get_effective_weight() 
                                for obj in objectives 
                                if obj.score is not None
                            ) / total_weight
                            evaluation.overall_score = round(weighted_score, 2)
                    
                    evaluation.status = 'COMPLETED'
                    evaluation.evaluation_completed_date = timezone.now()
                    evaluation.save()
                    completed_count += 1
        
        self.message_user(request, f'Se completaron {completed_count} evaluaciones.')
    complete_evaluation.short_description = 'Completar evaluaciones'


@admin.register(EvaluationObjective)
class EvaluationObjectiveAdmin(admin.ModelAdmin):
    list_display = [
        'evaluation', 'objective_title', 'objective_category', 
        'effective_weight', 'score', 'evaluated_at'
    ]
    list_filter = ['objective__category', 'evaluated_at', 'evaluation__quarter']
    search_fields = [
        'evaluation__employee__first_name', 'evaluation__employee__last_name',
        'objective__title'
    ]
    ordering = ['evaluation', 'objective__category__order', 'objective__title']
    readonly_fields = ['effective_weight', 'effective_description']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('evaluation', 'objective')
        }),
        ('Personalización', {
            'fields': ('custom_description', 'custom_weight', 'effective_description', 'effective_weight'),
            'classes': ('collapse',)
        }),
        ('Evaluación', {
            'fields': ('score', 'evaluator_comments', 'employee_comments', 'evaluated_at')
        }),
    )
    
    def objective_title(self, obj):
        return obj.objective.title
    objective_title.short_description = 'Objetivo'
    
    def objective_category(self, obj):
        return obj.objective.category.display_name
    objective_category.short_description = 'Categoría'
    
    def effective_weight(self, obj):
        return obj.get_effective_weight()
    effective_weight.short_description = 'Peso Efectivo'
    
    def effective_description(self, obj):
        return obj.get_effective_description()
    effective_description.short_description = 'Descripción Efectiva'


@admin.register(EvaluationAttachment)
class EvaluationAttachmentAdmin(admin.ModelAdmin):
    list_display = ['evaluation', 'filename', 'file_size_display', 'uploaded_by', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['evaluation__employee__first_name', 'evaluation__employee__last_name', 'filename']
    ordering = ['-uploaded_at']
    readonly_fields = ['uploaded_by', 'uploaded_at', 'file_size', 'file_size_display']
    
    def file_size_display(self, obj):
        """Mostrar tamaño de archivo en formato legible"""
        size = obj.file_size
        if size < 1024:
            return f'{size} bytes'
        elif size < 1024 * 1024:
            return f'{size / 1024:.1f} KB'
        else:
            return f'{size / (1024 * 1024):.1f} MB'
    file_size_display.short_description = 'Tamaño'