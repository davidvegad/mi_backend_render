#!/usr/bin/env python3
"""
Script para actualizar los roles de timehub con los nuevos permisos de aprobaciones
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from timehub.models import Role

def update_role_permissions():
    """
    Actualizar roles existentes con los nuevos permisos de aprobaciones
    """
    
    print("Actualizando permisos de roles existentes...")
    
    # Definir los permisos que cada rol debería tener
    role_permissions = {
        'ADMIN': [
            'view_timesheet', 'manage_timesheet', 
            'view_leave_requests', 'manage_leave_requests',
            'view_projects', 'manage_projects',
            'view_reports', 'manage_reports',
            'view_configuration', 'manage_configuration',
            'manage_users',
            'view_approvals', 'manage_approvals',  # Nuevos permisos
            'approve_timesheet', 'approve_leave_requests'
        ],
        'PROJECT_MANAGER': [
            'view_timesheet', 'manage_timesheet',
            'view_projects', 'manage_projects',
            'view_reports',
            'view_approvals', 'manage_approvals',  # Nuevos permisos
            'approve_timesheet', 'approve_leave_requests'
        ],
        'EMPLOYEE': [
            'view_timesheet', 'view_leave_requests',
            'view_approvals'  # Solo ver aprobaciones, no gestionar
        ]
    }
    
    updated_roles = []
    
    for role_code, permissions in role_permissions.items():
        try:
            role = Role.objects.get(code=role_code)
            # Actualizar permisos del rol
            role.permissions = permissions
            role.save()
            
            print(f"[OK] Rol '{role_code}' actualizado con {len(permissions)} permisos")
            updated_roles.append(role)
            
        except Role.DoesNotExist:
            print(f"[WARNING] Rol '{role_code}' no encontrado")
    
    return updated_roles

def create_missing_roles():
    """
    Crear roles que puedan estar faltando
    """
    print("\nVerificando roles faltantes...")
    
    roles_to_create = [
        {
            'code': 'SUPERVISOR',
            'name': 'Supervisor',
            'description': 'Supervisor de equipo con permisos de aprobación',
            'permissions': [
                'view_timesheet', 'view_leave_requests',
                'view_approvals', 'manage_approvals',
                'approve_timesheet', 'approve_leave_requests'
            ]
        },
        {
            'code': 'HR',
            'name': 'Recursos Humanos',
            'description': 'Personal de RRHH con permisos de gestión de personal',
            'permissions': [
                'view_timesheet', 'view_leave_requests', 'manage_leave_requests',
                'view_reports', 'manage_users',
                'view_approvals', 'manage_approvals',
                'approve_leave_requests'
            ]
        }
    ]
    
    created_roles = []
    
    for role_data in roles_to_create:
        role, created = Role.objects.get_or_create(
            code=role_data['code'],
            defaults={
                'name': role_data['name'],
                'description': role_data['description'],
                'permissions': role_data['permissions']
            }
        )
        
        if created:
            print(f"[OK] Creado rol: {role_data['code']} - {role_data['name']}")
            created_roles.append(role)
        else:
            print(f"[INFO] Ya existe rol: {role_data['code']}")
    
    return created_roles

def show_roles_summary():
    """
    Mostrar resumen de todos los roles y sus permisos
    """
    print("\n--- RESUMEN DE ROLES Y PERMISOS ---")
    
    roles = Role.objects.all().order_by('code')
    
    for role in roles:
        print(f"\nRol: {role.code} - {role.name}")
        print(f"Descripción: {role.description}")
        print("Permisos:")
        for perm in role.permissions:
            print(f"  - {perm}")

def main():
    """
    Función principal
    """
    print("Iniciando actualizacion de permisos de roles TimeHub\n")
    
    try:
        # Actualizar roles existentes
        updated_roles = update_role_permissions()
        
        # Crear roles faltantes
        created_roles = create_missing_roles()
        
        # Mostrar resumen
        show_roles_summary()
        
        print(f"\n[OK] Actualizacion completada!")
        print(f"Roles actualizados: {len(updated_roles)}")
        print(f"Roles creados: {len(created_roles)}")
        
        print("\nProximos pasos:")
        print("1. Asignar roles a usuarios según sea necesario")
        print("2. Verificar en el frontend que los permisos funcionan correctamente")
        print("3. Probar las funcionalidades de aprobación")
        
    except Exception as e:
        print(f"[ERROR] Error durante la actualizacion: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()