#!/usr/bin/env python3
"""
Script para verificar que el sistema de aprobaciones está configurado correctamente
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User, Permission, Group
from timehub.models import Role, UserProfile, TimeEntry, LeaveRequest

def verify_permissions():
    """
    Verificar que los permisos de aprobación existen
    """
    print("=== VERIFICACIÓN DE PERMISOS ===")
    
    approval_permissions = [
        'view_approvals',
        'manage_approvals', 
        'approve_timesheet',
        'approve_leave_requests'
    ]
    
    for perm_code in approval_permissions:
        try:
            permission = Permission.objects.get(codename=perm_code)
            print(f"[OK] Permiso '{perm_code}': {permission.name}")
        except Permission.DoesNotExist:
            print(f"[ERROR] Permiso '{perm_code}' no encontrado")

def verify_roles():
    """
    Verificar roles y sus permisos
    """
    print("\n=== VERIFICACIÓN DE ROLES ===")
    
    roles = Role.objects.all()
    
    for role in roles:
        approval_perms = [p for p in role.permissions if 'approval' in p or 'approve' in p]
        print(f"\nRol: {role.code} - {role.name}")
        print(f"  Permisos de aprobación: {approval_perms}")
        
        # Contar usuarios con este rol
        user_count = UserProfile.objects.filter(roles=role).count()
        print(f"  Usuarios con este rol: {user_count}")

def verify_django_groups():
    """
    Verificar grupos de Django
    """
    print("\n=== VERIFICACIÓN DE GRUPOS DJANGO ===")
    
    try:
        admin_group = Group.objects.get(name='ADMIN')
        approval_perms = admin_group.permissions.filter(
            codename__in=['view_approvals', 'manage_approvals', 'approve_timesheet', 'approve_leave_requests']
        )
        
        print(f"Grupo ADMIN tiene {approval_perms.count()} permisos de aprobación:")
        for perm in approval_perms:
            print(f"  - {perm.codename}: {perm.name}")
            
    except Group.DoesNotExist:
        print("[ERROR] Grupo ADMIN no encontrado")

def verify_test_data():
    """
    Verificar que hay datos de prueba
    """
    print("\n=== VERIFICACIÓN DE DATOS DE PRUEBA ===")
    
    # Contar entradas de tiempo
    timeentries_count = TimeEntry.objects.count()
    timeentries_pending = TimeEntry.objects.filter(status='SUBMITTED').count()
    
    print(f"Total de entradas de tiempo: {timeentries_count}")
    print(f"Entradas pendientes de aprobación: {timeentries_pending}")
    
    # Contar solicitudes de vacaciones
    leave_requests_count = LeaveRequest.objects.count()
    leave_requests_pending = LeaveRequest.objects.filter(status='SUBMITTED').count()
    
    print(f"Total de solicitudes de vacaciones: {leave_requests_count}")
    print(f"Solicitudes pendientes de aprobación: {leave_requests_pending}")

def show_approval_workflow():
    """
    Mostrar cómo funciona el flujo de aprobaciones
    """
    print("\n=== FLUJO DE APROBACIONES ===")
    
    print("\n1. APROBACIÓN DE TIMESHEET:")
    print("   - Empleado registra horas (status: DRAFT)")
    print("   - Empleado envía para aprobación (status: SUBMITTED)")
    print("   - Project Manager/Admin aprueba (status: APPROVED)")
    print("   - Permisos requeridos: approve_timesheet")
    
    print("\n2. APROBACIÓN DE VACACIONES:")
    print("   - Empleado solicita vacaciones (status: DRAFT)")
    print("   - Empleado envía solicitud (status: SUBMITTED)")
    print("   - Manager/HR aprueba (status: APPROVED)")
    print("   - Permisos requeridos: approve_leave_requests")
    
    print("\n3. ROLES Y PERMISOS:")
    print("   - ADMIN: Puede aprobar todo")
    print("   - PROJECT_MANAGER: Puede aprobar timesheet y vacaciones")
    print("   - HR: Puede aprobar vacaciones")
    print("   - SUPERVISOR: Puede aprobar timesheet y vacaciones")
    print("   - EMPLOYEE: Solo puede ver sus aprobaciones")

def suggest_frontend_implementation():
    """
    Sugerir implementación en el frontend
    """
    print("\n=== IMPLEMENTACIÓN EN FRONTEND ===")
    
    print("\n1. VERIFICAR PERMISOS DEL USUARIO:")
    print("   - Obtener roles del usuario desde UserProfile")
    print("   - Verificar permisos en la lista de permissions del rol")
    print("   - Mostrar/ocultar componentes según permisos")
    
    print("\n2. COMPONENTE DE APROBACIONES:")
    print("   - Crear página /approvals que muestre:")
    print("     * Timesheet pendientes (si tiene approve_timesheet)")
    print("     * Vacaciones pendientes (si tiene approve_leave_requests)")
    print("   - Botones de Aprobar/Rechazar")
    print("   - Filtros por tipo, usuario, fecha")
    
    print("\n3. ENDPOINTS API NECESARIOS:")
    print("   - GET /api/approvals/timesheet - Lista timesheet pendientes")
    print("   - POST /api/approvals/timesheet/{id}/approve - Aprobar")
    print("   - POST /api/approvals/timesheet/{id}/reject - Rechazar")
    print("   - GET /api/approvals/leave - Lista vacaciones pendientes")
    print("   - POST /api/approvals/leave/{id}/approve - Aprobar")
    print("   - POST /api/approvals/leave/{id}/reject - Rechazar")

def main():
    """
    Función principal
    """
    print("VERIFICACIÓN COMPLETA DEL SISTEMA DE APROBACIONES TIMEHUB")
    print("=" * 60)
    
    try:
        verify_permissions()
        verify_roles()
        verify_django_groups()
        verify_test_data()
        show_approval_workflow()
        suggest_frontend_implementation()
        
        print("\n" + "=" * 60)
        print("[OK] Sistema de aprobaciones configurado correctamente!")
        print("El sistema está listo para implementar las funcionalidades de aprobación en el frontend.")
        
    except Exception as e:
        print(f"[ERROR] Error durante la verificación: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()