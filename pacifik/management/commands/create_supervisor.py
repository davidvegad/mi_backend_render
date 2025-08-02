from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from pacifik.models import UserProfile
from django.db import transaction


class Command(BaseCommand):
    help = 'Crea un usuario supervisor o convierte un usuario existente en supervisor'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Email del usuario supervisor'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            help='Nombre del supervisor (solo para usuarios nuevos)'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            help='Apellido del supervisor (solo para usuarios nuevos)'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Contraseña del supervisor (solo para usuarios nuevos)'
        )
        parser.add_argument(
            '--convert',
            action='store_true',
            help='Convertir usuario existente en supervisor'
        )

    def handle(self, *args, **options):
        email = options['email']
        
        self.stdout.write(f'🔍 Buscando usuario con email: {email}')
        
        try:
            with transaction.atomic():
                try:
                    # Buscar usuario existente
                    user = User.objects.get(email=email)
                    existing_user = True
                    self.stdout.write(f'👤 Usuario encontrado: {user.get_full_name()}')
                    
                except User.DoesNotExist:
                    existing_user = False
                    
                    if options['convert']:
                        raise CommandError(f'❌ Usuario con email {email} no existe. No se puede convertir.')
                    
                    # Validar datos requeridos para nuevo usuario
                    if not all([options.get('first_name'), options.get('last_name'), options.get('password')]):
                        raise CommandError(
                            '❌ Para crear un nuevo supervisor necesitas: --first-name, --last-name, --password'
                        )
                    
                    # Crear nuevo usuario
                    self.stdout.write('👤 Creando nuevo usuario supervisor...')
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        first_name=options['first_name'],
                        last_name=options['last_name'],
                        password=options['password']
                    )
                    self.stdout.write(f'✅ Usuario creado: {user.get_full_name()}')
                
                # Obtener o crear perfil
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'numero_departamento': 'SUPERVISOR',
                        'role': 'supervisor',
                        'can_make_reservations': False,
                        'can_view_all_reservations': True,
                        'es_administrador': False
                    }
                )
                
                if not created:
                    # Actualizar perfil existente a supervisor
                    old_role = profile.role
                    profile.role = 'supervisor'
                    profile.can_make_reservations = False
                    profile.can_view_all_reservations = True
                    if profile.numero_departamento == '':
                        profile.numero_departamento = 'SUPERVISOR'
                    profile.save()
                    
                    if old_role != 'supervisor':
                        self.stdout.write(
                            f'🔄 Usuario convertido de {old_role} a supervisor'
                        )
                    else:
                        self.stdout.write('ℹ️  Usuario ya era supervisor')
                else:
                    self.stdout.write('✅ Perfil de supervisor creado')
                
                # Mostrar resumen
                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS('📋 RESUMEN DEL SUPERVISOR:'))
                self.stdout.write(f'📧 Email: {user.email}')
                self.stdout.write(f'👤 Nombre: {user.get_full_name()}')
                self.stdout.write(f'🏷️  Rol: {profile.get_role_display()}')
                self.stdout.write(f'🏠 Departamento: {profile.numero_departamento}')
                self.stdout.write('')
                self.stdout.write('🔐 PERMISOS:')
                self.stdout.write(f'   • Puede hacer reservas: ❌')
                self.stdout.write(f'   • Puede ver todas las reservas: ✅')
                self.stdout.write(f'   • Es administrador: {"✅" if profile.es_administrador else "❌"}')
                
                if not existing_user:
                    self.stdout.write('')
                    self.stdout.write(self.style.WARNING('🔑 CREDENCIALES DE ACCESO:'))
                    self.stdout.write(f'   Email: {email}')
                    self.stdout.write(f'   Contraseña: {options["password"]}')
                    self.stdout.write('')
                    self.stdout.write('⚠️  Guarda estas credenciales en un lugar seguro!')
                
                self.stdout.write('')
                self.stdout.write(
                    self.style.SUCCESS('✅ Supervisor configurado exitosamente!')
                )
                
        except Exception as e:
            raise CommandError(f'❌ Error al crear supervisor: {e}')

    def get_example_usage(self):
        return """
Ejemplos de uso:

1. Crear nuevo supervisor:
   python manage.py create_supervisor --email supervisor@pacifik.com --first-name "Ana" --last-name "García" --password "supervisor123"

2. Convertir usuario existente en supervisor:
   python manage.py create_supervisor --email usuario@example.com --convert
        """