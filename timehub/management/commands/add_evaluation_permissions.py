# Comando para agregar permisos de evaluación a roles existentes
from django.core.management.base import BaseCommand
from timehub.models import Role


class Command(BaseCommand):
    help = 'Agrega permisos del sistema de evaluación a roles existentes'

    def handle(self, *args, **options):
        self.stdout.write('Agregando permisos de evaluación a roles existentes...')
        
        # Permisos del sistema de evaluación
        evaluation_permissions = [
            'view_evaluations',      # Ver evaluaciones
            'manage_evaluations',    # Gestionar evaluaciones (evaluar empleados)
            'assign_objectives',     # Asignar objetivos a empleados
        ]
        
        # Obtener roles existentes
        try:
            admin_role = Role.objects.get(code='ADMIN')
            hr_role = Role.objects.get(code='HR')
            
            # ADMIN: Todos los permisos
            admin_permissions = set(admin_role.permissions)
            for perm in evaluation_permissions:
                admin_permissions.add(perm)
            admin_role.permissions = list(admin_permissions)
            admin_role.save()
            
            self.stdout.write(f'✅ Agregados permisos de evaluación al rol ADMIN')
            
            # HR: Todos los permisos de evaluación
            hr_permissions = set(hr_role.permissions)
            for perm in evaluation_permissions:
                hr_permissions.add(perm)
            hr_role.permissions = list(hr_permissions)
            hr_role.save()
            
            self.stdout.write(f'✅ Agregados permisos de evaluación al rol HR')
            
            # Manager: Solo view_evaluations y manage_evaluations (no assign_objectives)
            try:
                manager_role = Role.objects.get(code='MANAGER')
                manager_permissions = set(manager_role.permissions)
                manager_permissions.add('view_evaluations')
                manager_permissions.add('manage_evaluations')
                manager_role.permissions = list(manager_permissions)
                manager_role.save()
                
                self.stdout.write(f'✅ Agregados permisos de evaluación al rol MANAGER')
                
            except Role.DoesNotExist:
                self.stdout.write(f'⚠️  Rol MANAGER no encontrado, se omite')
            
            # Lead: Solo view_evaluations y manage_evaluations
            try:
                lead_role = Role.objects.get(code='LEAD')
                lead_permissions = set(lead_role.permissions)
                lead_permissions.add('view_evaluations')
                lead_permissions.add('manage_evaluations')
                lead_role.permissions = list(lead_permissions)
                lead_role.save()
                
                self.stdout.write(f'✅ Agregados permisos de evaluación al rol LEAD')
                
            except Role.DoesNotExist:
                self.stdout.write(f'⚠️  Rol LEAD no encontrado, se omite')
            
        except Role.DoesNotExist as e:
            self.stdout.write(f'❌ Error: No se encontró el rol requerido: {e}')
            return
        
        self.stdout.write(self.style.SUCCESS('✅ Permisos de evaluación agregados exitosamente!'))
        self.stdout.write('')
        self.stdout.write('Distribución de permisos:')
        self.stdout.write('- ADMIN: view_evaluations, manage_evaluations, assign_objectives')
        self.stdout.write('- HR: view_evaluations, manage_evaluations, assign_objectives')
        self.stdout.write('- MANAGER: view_evaluations, manage_evaluations')
        self.stdout.write('- LEAD: view_evaluations, manage_evaluations')
        self.stdout.write('')
        self.stdout.write('Puedes verificar y modificar permisos desde:')
        self.stdout.write('Django Admin -> Roles -> [Seleccionar rol] -> Permissions')