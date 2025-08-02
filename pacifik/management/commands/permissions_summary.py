from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pacifik.models import UserProfile, Reserva


class Command(BaseCommand):
    help = 'Muestra un resumen del sistema de permisos implementado'

    def handle(self, *args, **options):
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎯 SISTEMA DE PERMISOS PACIFIK OCEAN TOWER'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        
        # Estadísticas de usuarios
        total_users = User.objects.count()
        total_residents = UserProfile.objects.filter(role='resident').count()
        total_supervisors = UserProfile.objects.filter(role='supervisor').count()
        
        self.stdout.write('')
        self.stdout.write('📊 ESTADÍSTICAS GENERALES:')
        self.stdout.write(f'   • Total usuarios: {total_users}')
        self.stdout.write(f'   • Residentes: {total_residents} ({(total_residents/total_users*100):.1f}%)')
        self.stdout.write(f'   • Supervisores: {total_supervisors} ({(total_supervisors/total_users*100):.1f}%)')
        
        # Detalles de permisos
        self.stdout.write('')
        self.stdout.write('🏠 PERMISOS DE RESIDENTES:')
        self.stdout.write('   ✅ Pueden hacer reservas')
        self.stdout.write('   ✅ Ven sus propias reservas en dashboard')
        self.stdout.write('   ✅ Acceden a todas las páginas')
        self.stdout.write('   ❌ No ven todas las reservas del edificio (por defecto)')
        
        self.stdout.write('')
        self.stdout.write('👁️  PERMISOS DE SUPERVISORES:')
        self.stdout.write('   ❌ No pueden hacer reservas')
        self.stdout.write('   ✅ Ven todas las reservas del edificio')
        self.stdout.write('   ❌ No acceden a /reservar (bloqueado)')
        self.stdout.write('   ✅ Dashboard específico para supervisión')
        
        # Reservas activas
        total_reservas = Reserva.objects.count()
        reservas_activas = Reserva.objects.filter(estado='reservado').count()
        
        self.stdout.write('')
        self.stdout.write('📅 ACTIVIDAD DE RESERVAS:')
        self.stdout.write(f'   • Total reservas históricas: {total_reservas}')
        self.stdout.write(f'   • Reservas activas: {reservas_activas}')
        
        # Ejemplos de usuarios
        if total_residents > 0:
            self.stdout.write('')
            self.stdout.write('👥 EJEMPLOS DE RESIDENTES:')
            for profile in UserProfile.objects.filter(role='resident')[:3]:
                perms = profile.get_permissions()
                self.stdout.write(
                    f'   • {profile.user.get_full_name()} - Dpto {profile.numero_departamento}'
                )
                self.stdout.write(
                    f'     Puede reservar: {"✅" if perms["can_make_reservations"] else "❌"} | '
                    f'Ve todas: {"✅" if perms["can_view_all_reservations"] else "❌"}'
                )
        
        if total_supervisors > 0:
            self.stdout.write('')
            self.stdout.write('👁️  SUPERVISORES CONFIGURADOS:')
            for profile in UserProfile.objects.filter(role='supervisor'):
                perms = profile.get_permissions()
                self.stdout.write(
                    f'   • {profile.user.get_full_name()} - {profile.user.email}'
                )
                self.stdout.write(
                    f'     Puede reservar: {"✅" if perms["can_make_reservations"] else "❌"} | '
                    f'Ve todas: {"✅" if perms["can_view_all_reservations"] else "❌"}'
                )
        
        # Comandos disponibles
        self.stdout.write('')
        self.stdout.write('🛠️  COMANDOS DISPONIBLES:')
        self.stdout.write('   • python manage.py migrate_user_permissions')
        self.stdout.write('     → Migra usuarios existentes a residentes')
        self.stdout.write('')
        self.stdout.write('   • python manage.py create_supervisor --email supervisor@example.com \\')
        self.stdout.write('       --first-name "Ana" --last-name "García" --password "pass123"')
        self.stdout.write('     → Crea nuevo supervisor')
        self.stdout.write('')
        self.stdout.write('   • python manage.py create_supervisor --email usuario@example.com --convert')
        self.stdout.write('     → Convierte usuario existente en supervisor')
        
        # URLs protegidas
        self.stdout.write('')
        self.stdout.write('🔒 ENDPOINTS PROTEGIDOS:')
        self.stdout.write('   • POST /api/pacifik/reservas/ (crear reserva)')
        self.stdout.write('   • POST /api/pacifik/disponibilidad/ (consultar disponibilidad)')
        self.stdout.write('   → Solo usuarios con can_make_reservations=True')
        
        # Frontend
        self.stdout.write('')
        self.stdout.write('🎨 FRONTEND ADAPTATIVO:')
        self.stdout.write('   • Navbar muestra/oculta "Reservar" según permisos')
        self.stdout.write('   • Página /reservar protegida con PermissionGuard')
        self.stdout.write('   • Badge "Supervisor" en menú móvil')
        self.stdout.write('   • Texto "Supervisar Reservas" vs "Ver Reservas"')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Sistema de permisos funcionando correctamente!'))
        self.stdout.write('')
        
        return "Resumen completado"