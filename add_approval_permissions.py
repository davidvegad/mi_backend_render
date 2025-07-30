#!/usr/bin/env python3
"""
Script para agregar permisos de aprobaciones al sistema TimeHub
Ejecutar desde el directorio del proyecto backend de Django
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

def create_approval_permissions():
    """
    Crear permisos personalizados para el sistema de aprobaciones
    """
    
    print("Creando permisos de aprobaciones...")
    
    # Obtener el modelo User o crear un ContentType genérico
    try:
        # Intentar obtener el modelo TimeEntry si existe
        time_entry_model = apps.get_model('timehub', 'TimeEntry')
        time_entry_ct = ContentType.objects.get_for_model(time_entry_model)
    except:
        # Si no existe, usar el modelo User
        from django.contrib.auth.models import User
        time_entry_ct = ContentType.objects.get_for_model(User)
    
    try:
        # Intentar obtener el modelo LeaveRequest si existe  
        leave_request_model = apps.get_model('timehub', 'LeaveRequest')
        leave_request_ct = ContentType.objects.get_for_model(leave_request_model)
    except:
        # Si no existe, usar el modelo User
        from django.contrib.auth.models import User
        leave_request_ct = ContentType.objects.get_for_model(User)
    
    # Definir los permisos a crear
    permissions_to_create = [
        {
            'codename': 'view_approvals',
            'name': 'Can view approval requests',
            'content_type': time_entry_ct,
            'description': 'Permite ver las solicitudes pendientes de aprobación'
        },
        {
            'codename': 'manage_approvals', 
            'name': 'Can manage approval requests',
            'content_type': time_entry_ct,
            'description': 'Permite aprobar o rechazar solicitudes'
        },
        {
            'codename': 'approve_timesheet',
            'name': 'Can approve timesheet entries',
            'content_type': time_entry_ct,
            'description': 'Permite aprobar entradas de tiempo'
        },
        {
            'codename': 'approve_leave_requests',
            'name': 'Can approve leave requests', 
            'content_type': leave_request_ct,
            'description': 'Permite aprobar solicitudes de vacaciones'
        }
    ]
    
    created_permissions = []
    
    for perm_data in permissions_to_create:
        permission, created = Permission.objects.get_or_create(
            codename=perm_data['codename'],
            content_type=perm_data['content_type'],
            defaults={
                'name': perm_data['name']
            }
        )
        
        if created:
            print(f"[OK] Creado permiso: {perm_data['codename']} - {perm_data['name']}")
            created_permissions.append(permission)
        else:
            print(f"[INFO] Ya existe permiso: {perm_data['codename']}")
    
    return created_permissions

def assign_permissions_to_roles():
    """
    Asignar permisos a roles existentes
    """
    print("\nAsignando permisos a roles...")
    
    try:
        from django.contrib.auth.models import Group
        
        # Buscar roles/grupos existentes que deberían tener permisos de aprobación
        roles_to_check = ['ADMIN', 'RRHH', 'Manager', 'Supervisor', 'HR']
        
        approval_permissions = Permission.objects.filter(
            codename__in=['view_approvals', 'manage_approvals', 'approve_timesheet', 'approve_leave_requests']
        )
        
        for role_name in roles_to_check:
            try:
                role = Group.objects.get(name=role_name)
                
                # Agregar todos los permisos de aprobación
                for permission in approval_permissions:
                    role.permissions.add(permission)
                
                print(f"[OK] Permisos asignados al rol: {role_name}")
                
            except Group.DoesNotExist:
                print(f"[WARNING] Rol no encontrado: {role_name}")
        
    except Exception as e:
        print(f"[ERROR] Error asignando permisos a roles: {str(e)}")

def create_sample_admin_user():
    """
    Crear un usuario admin de ejemplo con todos los permisos
    """
    print("\nVerificando usuario admin...")
    
    try:
        from django.contrib.auth.models import User, Group
        
        # Crear o obtener grupo ADMIN
        admin_group, created = Group.objects.get_or_create(name='ADMIN')
        if created:
            print("[OK] Creado grupo ADMIN")
        
        # Asignar todos los permisos de aprobación al grupo ADMIN
        approval_permissions = Permission.objects.filter(
            codename__in=['view_approvals', 'manage_approvals', 'approve_timesheet', 'approve_leave_requests']
        )
        
        for permission in approval_permissions:
            admin_group.permissions.add(permission)
        
        print("[OK] Permisos de aprobación asignados al grupo ADMIN")
        
    except Exception as e:
        print(f"[ERROR] Error configurando admin: {str(e)}")

def main():
    """
    Función principal
    """
    print("Iniciando configuracion de permisos de aprobaciones TimeHub\n")
    
    try:
        # Crear permisos
        created_permissions = create_approval_permissions()
        
        # Asignar permisos a roles
        assign_permissions_to_roles()
        
        # Configurar admin
        create_sample_admin_user()
        
        print(f"\n[OK] Configuracion completada exitosamente!")
        print(f"Permisos creados: {len(created_permissions)}")
        
        print("\nPermisos disponibles para usar en el frontend:")
        print("   - view_approvals")
        print("   - manage_approvals") 
        print("   - approve_timesheet")
        print("   - approve_leave_requests")
        
        print("\nProximos pasos:")
        print("   1. Verificar que los roles existen en tu sistema")
        print("   2. Asignar permisos a usuarios específicos si es necesario")
        print("   3. Reiniciar el servidor Django")
        print("   4. Verificar en el frontend que los permisos funcionan")
        
    except Exception as e:
        print(f"[ERROR] Error durante la configuracion: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()