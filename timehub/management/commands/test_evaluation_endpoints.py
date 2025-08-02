# Comando para probar endpoints de evaluación
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from timehub.models import UserProfile
from timehub.models_evaluation import ObjectiveCategory, EvaluationRole, Quarter, Objective


class Command(BaseCommand):
    help = 'Prueba los endpoints de evaluación y muestra el estado de los datos'

    def handle(self, *args, **options):
        self.stdout.write('=== ESTADO DEL SISTEMA DE EVALUACIÓN ===')
        
        # Verificar modelos básicos
        self.stdout.write('\n📊 CONTEO DE REGISTROS:')
        try:
            categories_count = ObjectiveCategory.objects.count()
            self.stdout.write(f'- Categorías: {categories_count}')
        except Exception as e:
            self.stdout.write(f'❌ Error categorías: {e}')
            
        try:
            roles_count = EvaluationRole.objects.count()
            self.stdout.write(f'- Roles de evaluación: {roles_count}')
        except Exception as e:
            self.stdout.write(f'❌ Error roles: {e}')
            
        try:
            quarters_count = Quarter.objects.count()
            self.stdout.write(f'- Trimestres: {quarters_count}')
        except Exception as e:
            self.stdout.write(f'❌ Error trimestres: {e}')
            
        try:
            objectives_count = Objective.objects.count()
            self.stdout.write(f'- Objetivos: {objectives_count}')
        except Exception as e:
            self.stdout.write(f'❌ Error objetivos: {e}')
        
        # Verificar usuarios
        self.stdout.write('\n👥 USUARIOS:')
        try:
            users_count = User.objects.filter(is_active=True).count()
            self.stdout.write(f'- Usuarios activos: {users_count}')
            
            profiles_count = UserProfile.objects.filter(is_active=True).count()
            self.stdout.write(f'- Perfiles activos: {profiles_count}')
            
            # Mostrar algunos usuarios de ejemplo
            sample_users = User.objects.filter(is_active=True)[:3]
            for user in sample_users:
                profile_status = "✅" if hasattr(user, 'timehub_profile') and user.timehub_profile.is_active else "❌"
                self.stdout.write(f'  - {user.username} ({user.get_full_name()}) {profile_status}')
                
        except Exception as e:
            self.stdout.write(f'❌ Error usuarios: {e}')
        
        # Verificar datos de ejemplo específicos
        self.stdout.write('\n🎯 DATOS DE EJEMPLO:')
        try:
            if Quarter.objects.filter(is_active=True).exists():
                active_quarter = Quarter.objects.get(is_active=True)
                self.stdout.write(f'✅ Trimestre activo: {active_quarter}')
            else:
                self.stdout.write('⚠️  No hay trimestre activo')
                
            if EvaluationRole.objects.filter(name='Desarrollador Senior').exists():
                dev_senior = EvaluationRole.objects.get(name='Desarrollador Senior')
                objectives_count = dev_senior.objectives.count()
                self.stdout.write(f'✅ Rol "Desarrollador Senior" con {objectives_count} objetivos')
            else:
                self.stdout.write('⚠️  No existe rol "Desarrollador Senior"')
                
        except Exception as e:
            self.stdout.write(f'❌ Error datos ejemplo: {e}')
        
        # Probar consultas problemáticas
        self.stdout.write('\n🔍 PRUEBAS DE CONSULTAS:')
        try:
            # Simular consulta de empleados
            from timehub.models import UserProfile
            employee_profiles = UserProfile.objects.filter(
                is_active=True,
                user__is_active=True
            ).select_related('user')[:5]
            
            self.stdout.write(f'✅ Consulta empleados: {len(employee_profiles)} encontrados')
            for profile in employee_profiles:
                self.stdout.write(f'  - {profile.user.get_full_name() or profile.user.username}')
                
        except Exception as e:
            self.stdout.write(f'❌ Error consulta empleados: {e}')
            
        try:
            # Simular consulta de supervisores
            supervisor_profiles = UserProfile.objects.filter(
                is_active=True,
                user__is_active=True
            ).select_related('user')[:5]
            
            self.stdout.write(f'✅ Consulta supervisores: {len(supervisor_profiles)} encontrados')
                
        except Exception as e:
            self.stdout.write(f'❌ Error consulta supervisores: {e}')
        
        self.stdout.write('\n=== FIN DEL DIAGNÓSTICO ===')
        
        # Sugerencias
        self.stdout.write('\n💡 SUGERENCIAS:')
        if ObjectiveCategory.objects.count() == 0:
            self.stdout.write('1. Ejecutar: python manage.py create_evaluation_sample_data')
        if UserProfile.objects.count() == 0:
            self.stdout.write('2. Crear perfiles de usuario desde el admin')
        if Quarter.objects.filter(is_active=True).count() == 0:
            self.stdout.write('3. Activar un trimestre desde la configuración')