# Modelos para el sistema de evaluación trimestral de personal
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class EvaluationRole(models.Model):
    """Roles para evaluación (ej: Desarrollador Senior, Analista, etc.)"""
    name = models.CharField(max_length=100, verbose_name="Nombre del Rol")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rol de Evaluación"
        verbose_name_plural = "Roles de Evaluación"

    def __str__(self):
        return self.name


class ObjectiveCategory(models.Model):
    """Categorías de objetivos: Desempeño Técnico, Colaboración y Equipo, Formación-Crecimiento"""
    CATEGORIES = [
        ('TECHNICAL', 'Desempeño Técnico'),
        ('COLLABORATION', 'Colaboración y Equipo'),
        ('GROWTH', 'Formación - Crecimiento'),
    ]
    
    name = models.CharField(max_length=20, choices=CATEGORIES, unique=True, verbose_name="Categoría")
    display_name = models.CharField(max_length=100, verbose_name="Nombre para Mostrar")
    description = models.TextField(blank=True, verbose_name="Descripción")
    order = models.IntegerField(default=0, verbose_name="Orden de Visualización")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoría de Objetivo"
        verbose_name_plural = "Categorías de Objetivos"
        ordering = ['order']

    def __str__(self):
        return self.display_name


class Objective(models.Model):
    """Objetivos específicos por rol y categoría"""
    role = models.ForeignKey(EvaluationRole, on_delete=models.CASCADE, verbose_name="Rol")
    category = models.ForeignKey(ObjectiveCategory, on_delete=models.CASCADE, verbose_name="Categoría")
    title = models.CharField(max_length=200, verbose_name="Título del Objetivo")
    description = models.TextField(verbose_name="Descripción Detallada")
    weight = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('1.00'), 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Peso del Objetivo",
        help_text="Importancia relativa del objetivo (usado para cálculos ponderados)"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Objetivo"
        verbose_name_plural = "Objetivos"
        ordering = ['role', 'category', 'title']
        unique_together = ['role', 'category', 'title']

    def __str__(self):
        return f"{self.role.name} - {self.category.display_name}: {self.title}"


class Quarter(models.Model):
    """Trimestres de evaluación"""
    QUARTERS = [
        ('Q1', 'Primer Trimestre'),
        ('Q2', 'Segundo Trimestre'),
        ('Q3', 'Tercer Trimestre'),
        ('Q4', 'Cuarto Trimestre'),
    ]
    
    year = models.IntegerField(verbose_name="Año")
    quarter = models.CharField(max_length=2, choices=QUARTERS, verbose_name="Trimestre")
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Fin")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Trimestre"
        verbose_name_plural = "Trimestres"
        unique_together = ['year', 'quarter']
        ordering = ['-year', '-quarter']

    def __str__(self):
        return f"{self.get_quarter_display()} {self.year}"
    
    @property
    def quarter_display(self):
        """Devuelve el nombre del trimestre para mostrar"""
        return self.get_quarter_display()


class EmployeeEvaluation(models.Model):
    """Evaluación asignada a un empleado para un trimestre específico"""
    STATUSES = [
        ('ASSIGNED', 'Objetivos Asignados'),
        ('OBJECTIVES_SENT', 'Objetivos Enviados'),
        ('IN_PROGRESS', 'En Progreso'),
        ('PENDING_REVIEW', 'Pendiente de Revisión'),
        ('COMPLETED', 'Completada'),
        ('CANCELLED', 'Cancelada'),
    ]
    
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluations', verbose_name="Empleado")
    quarter = models.ForeignKey(Quarter, on_delete=models.CASCADE, verbose_name="Trimestre")
    role = models.ForeignKey(EvaluationRole, on_delete=models.CASCADE, verbose_name="Rol Asignado")
    supervisor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='supervised_evaluations', 
        verbose_name="Jefe de Proyecto"
    )
    status = models.CharField(max_length=20, choices=STATUSES, default='ASSIGNED', verbose_name="Estado")
    
    # Fechas importantes
    assigned_date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Asignación")
    objectives_sent_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Envío de Objetivos")
    evaluation_completed_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Evaluación Completada")
    
    # Notas generales
    assignment_notes = models.TextField(blank=True, verbose_name="Notas de Asignación")
    evaluation_notes = models.TextField(blank=True, verbose_name="Notas de Evaluación")
    
    # Métricas calculadas
    overall_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name="Puntuación General (%)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Evaluación de Empleado"
        verbose_name_plural = "Evaluaciones de Empleados"
        unique_together = ['employee', 'quarter']
        ordering = ['-quarter__year', '-quarter__quarter', 'employee__last_name']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.quarter} ({self.get_status_display()})"


class EvaluationObjective(models.Model):
    """Objetivos específicos asignados a una evaluación de empleado"""
    evaluation = models.ForeignKey(
        EmployeeEvaluation, 
        on_delete=models.CASCADE, 
        related_name='objectives',
        verbose_name="Evaluación"
    )
    objective = models.ForeignKey(Objective, on_delete=models.CASCADE, verbose_name="Objetivo")
    
    # Personalización del objetivo para esta evaluación específica
    custom_description = models.TextField(
        blank=True, 
        verbose_name="Descripción Personalizada",
        help_text="Si se especifica, reemplaza la descripción del objetivo base"
    )
    custom_weight = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Peso Personalizado"
    )
    
    # Evaluación (se completa al final del trimestre)
    score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name="Calificación (%)"
    )
    evaluator_comments = models.TextField(blank=True, verbose_name="Comentarios del Evaluador")
    employee_comments = models.TextField(blank=True, verbose_name="Comentarios del Empleado")
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    evaluated_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Evaluación")

    class Meta:
        verbose_name = "Objetivo de Evaluación"
        verbose_name_plural = "Objetivos de Evaluación"
        unique_together = ['evaluation', 'objective']
        ordering = ['objective__category__order', 'objective__title']

    def get_effective_description(self):
        """Retorna la descripción personalizada o la del objetivo base"""
        return self.custom_description or self.objective.description

    def get_effective_weight(self):
        """Retorna el peso personalizado o el del objetivo base"""
        return self.custom_weight or self.objective.weight

    def __str__(self):
        return f"{self.evaluation.employee.get_full_name()} - {self.objective.title}"


class EvaluationAttachment(models.Model):
    """Adjuntos enviados con los objetivos"""
    evaluation = models.ForeignKey(
        EmployeeEvaluation, 
        on_delete=models.CASCADE, 
        related_name='attachments',
        verbose_name="Evaluación"
    )
    file = models.FileField(upload_to='evaluation_attachments/', verbose_name="Archivo")
    filename = models.CharField(max_length=255, verbose_name="Nombre del Archivo")
    file_size = models.BigIntegerField(verbose_name="Tamaño del Archivo (bytes)")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Subido por")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Subida")
    
    class Meta:
        verbose_name = "Adjunto de Evaluación"
        verbose_name_plural = "Adjuntos de Evaluación"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.evaluation} - {self.filename}"