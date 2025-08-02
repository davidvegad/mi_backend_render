from django.core.management.base import BaseCommand
from django.utils import timezone
from pacifik.models import UserProfile


class Command(BaseCommand):
    help = 'Migra todos los usuarios existentes para configurar permisos por defecto'

    def handle(self, *args, **options):
        """Configurar permisos por defecto para usuarios existentes"""
        
        self.stdout.write(
            self.style.SUCCESS('🔄 Iniciando migración de permisos de usuarios...')
        )
        
        # Obtener todos los perfiles de usuario que no tienen rol definido
        profiles_sin_rol = UserProfile.objects.filter(role__isnull=True)
        count_sin_rol = profiles_sin_rol.count()
        
        self.stdout.write(f'📊 Encontrados {count_sin_rol} usuarios sin rol definido')
        
        if count_sin_rol > 0:
            # Actualizar usuarios sin rol a 'resident' con permisos por defecto
            profiles_sin_rol.update(
                role='resident',
                can_make_reservations=True,
                can_view_all_reservations=False
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ {count_sin_rol} usuarios configurados como residentes con permisos de reserva'
                )
            )
        
        # Obtener estadísticas finales
        total_residents = UserProfile.objects.filter(role='resident').count()
        total_supervisors = UserProfile.objects.filter(role='supervisor').count()
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('📈 RESUMEN DE PERMISOS:'))
        self.stdout.write(f'🏠 Residentes: {total_residents}')
        self.stdout.write(f'👁️  Supervisores: {total_supervisors}')
        self.stdout.write('')
        
        # Mostrar algunos ejemplos de usuarios
        if total_residents > 0:
            self.stdout.write('👥 EJEMPLOS DE RESIDENTES:')
            for profile in UserProfile.objects.filter(role='resident')[:3]:
                self.stdout.write(
                    f'   • {profile.user.get_full_name()} - Dpto {profile.numero_departamento}'
                )
        
        if total_supervisors > 0:
            self.stdout.write('')
            self.stdout.write('👁️  SUPERVISORES ACTUALES:')
            for profile in UserProfile.objects.filter(role='supervisor'):
                self.stdout.write(
                    f'   • {profile.user.get_full_name()} - {profile.user.email}'
                )
        
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS('✅ Migración completada exitosamente!')
        )
        
        return f"Migración completada: {total_residents} residentes, {total_supervisors} supervisores"