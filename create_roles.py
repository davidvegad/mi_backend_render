#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('.')
django.setup()

from timehub.models import Role

def create_basic_roles():
    """Crear roles básicos del sistema"""
    
    roles_data = [
        {
            'name': 'Empleado',
            'code': 'EMPLOYEE',
            'description': 'Usuario básico con acceso a timesheet y vacaciones',
            'permissions': ['view_timesheet', 'view_leave_requests'],
            'is_active': True
        },
        {
            'name': 'Project Manager',
            'code': 'PROJECT_MANAGER',
            'description': 'Gestiona proyectos y reportes',
            'permissions': [
                'view_timesheet', 'manage_timesheet', 
                'view_projects', 'manage_projects', 
                'view_reports'
            ],
            'is_active': True
        },
        {
            'name': 'Administrador',
            'code': 'ADMIN',
            'description': 'Acceso completo al sistema',
            'permissions': [
                'view_timesheet', 'manage_timesheet', 
                'view_leave_requests', 'manage_leave_requests',
                'view_projects', 'manage_projects', 
                'view_reports', 'manage_reports',
                'view_configuration', 'manage_configuration', 
                'manage_users'
            ],
            'is_active': True
        }
    ]
    
    for role_data in roles_data:
        role, created = Role.objects.get_or_create(
            code=role_data['code'],
            defaults=role_data
        )
        
        if created:
            print(f"[OK] Rol creado: {role.name} ({role.code})")
        else:
            print(f"[INFO] Rol ya existe: {role.name} ({role.code})")
    
    print(f"\nTotal de roles en el sistema: {Role.objects.count()}")

if __name__ == '__main__':
    create_basic_roles()