from django.core.management.base import BaseCommand
from pacifik.models import Area, Reserva

class Command(BaseCommand):
    help = 'Resetea todas las áreas comunes (CUIDADO: elimina reservas activas)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirma que quieres resetear todas las áreas',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  ADVERTENCIA: Este comando eliminará todas las áreas y reservas.\n'
                    'Usa --confirm para ejecutar el reseteo.'
                )
            )
            return

        # Eliminar todas las reservas
        reservas_count = Reserva.objects.count()
        Reserva.objects.all().delete()
        
        # Eliminar todas las áreas
        areas_count = Area.objects.count()
        Area.objects.all().delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🗑️  Reseteo completado:\n'
                f'- {reservas_count} reservas eliminadas\n'
                f'- {areas_count} áreas eliminadas'
            )
        )
        
        # Llamar al comando de inicialización
        from django.core.management import call_command
        call_command('initialize_areas')
        
        self.stdout.write(
            self.style.SUCCESS('✅ Áreas reinicializadas correctamente')
        )