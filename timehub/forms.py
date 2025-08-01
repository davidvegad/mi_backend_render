from django import forms
from django.contrib import admin
from .models import Role


class PermissionsWidget(forms.CheckboxSelectMultiple):
    """Widget personalizado para mostrar permisos como checkboxes"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({'class': 'permissions-checkboxes'})


class RoleAdminForm(forms.ModelForm):
    """Formulario personalizado para Role con widget de permisos mejorado"""
    
    # Definición completa de permisos disponibles
    PERMISSION_CHOICES = [
        # Timesheet
        ('view_timesheet', 'Ver Timesheet'),
        ('manage_timesheet', 'Gestionar Timesheet'),
        
        # Proyectos
        ('view_projects', 'Ver Proyectos'),
        ('manage_projects', 'Gestionar Proyectos'),
        
        # Solicitudes de Permisos
        ('view_leave_requests', 'Ver Solicitudes de Permisos'),
        ('manage_leave_requests', 'Gestionar Solicitudes de Permisos'),
        
        # Aprobaciones
        ('view_approvals', 'Ver Aprobaciones'),
        ('manage_approvals', 'Gestionar Aprobaciones'),
        ('approve_timesheet', 'Aprobar Timesheet'),
        ('approve_leave_requests', 'Aprobar Solicitudes de Permisos'),
        
        # Reportes
        ('view_reports', 'Ver Reportes'),
        ('manage_reports', 'Gestionar Reportes'),
        
        # Configuración
        ('view_configuration', 'Ver Configuración'),
        ('manage_configuration', 'Gestionar Configuración'),
        ('manage_users', 'Gestionar Usuarios'),
        ('view_admin', 'Ver Panel de Administración'),
        
        # Sistema de Evaluación
        ('view_evaluations', 'Ver Evaluaciones'),
        ('manage_evaluations', 'Gestionar Evaluaciones (Evaluar Personal)'),
        ('assign_objectives', 'Asignar Objetivos a Empleados'),
    ]
    
    permissions = forms.MultipleChoiceField(
        choices=PERMISSION_CHOICES,
        widget=PermissionsWidget,
        required=False,
        help_text="Selecciona los permisos que tendrá este rol"
    )
    
    class Meta:
        model = Role
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si estamos editando un rol existente, pre-seleccionar permisos
        if self.instance and self.instance.pk:
            self.fields['permissions'].initial = self.instance.permissions or []
    
    def clean_permissions(self):
        """Validar y procesar permisos seleccionados"""
        permissions = self.cleaned_data.get('permissions', [])
        return list(permissions)  # Convertir a lista para JSONField
    
    def save(self, commit=True):
        """Guardar permisos en formato correcto"""
        instance = super().save(commit=False)
        
        # Asegurar que permissions sea una lista
        permissions = self.cleaned_data.get('permissions', [])
        instance.permissions = list(permissions)
        
        if commit:
            instance.save()
        return instance