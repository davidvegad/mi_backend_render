"""
Comando de management para acumular días de vacaciones no utilizados
al final del año.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from timehub.utils import process_year_end_accumulation


class Command(BaseCommand):
    help = 'Acumula días de vacaciones no utilizados al final del año'

    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            type=int,
            default=timezone.now().year - 1,
            help='Año para procesar (por defecto: año anterior)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo mostrar lo que se haría sin guardar cambios'
        )

    def handle(self, *args, **options):
        year = options['year']
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS(f'🚀 Procesando acumulación de días de vacaciones para el año {year}...')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('⚠️  MODO DRY-RUN: No se guardarán cambios')
            )
        
        try:
            if not dry_run:
                result = process_year_end_accumulation(year)
            else:
                # Para dry-run, simulamos el proceso sin guardar
                from timehub.models import UserProfile
                from timehub.utils import calculate_accumulated_vacation_days
                
                result = {
                    'year_processed': year,
                    'users_processed': 0,
                    'total_days_accumulated': 0.0
                }
                
                user_profiles = UserProfile.objects.filter(is_active=True)
                
                for profile in user_profiles:
                    days_to_accumulate = calculate_accumulated_vacation_days(profile.user.id, year)
                    
                    if days_to_accumulate > 0:
                        result['users_processed'] += 1
                        result['total_days_accumulated'] += days_to_accumulate
                        
                        self.stdout.write(
                            f"  📊 {profile.user.username}: {days_to_accumulate} días"
                        )
                
                result['average_per_user'] = (
                    result['total_days_accumulated'] / result['users_processed'] 
                    if result['users_processed'] > 0 else 0
                )
            
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('✅ Procesamiento completado:'))
            self.stdout.write(f"  📅 Año procesado: {result['year_processed']}")
            self.stdout.write(f"  👥 Usuarios procesados: {result['users_processed']}")
            self.stdout.write(f"  📈 Total días acumulados: {result['total_days_accumulated']:.1f}")
            
            if result['users_processed'] > 0:
                self.stdout.write(f"  📊 Promedio por usuario: {result['average_per_user']:.1f} días")
            
            if not dry_run:
                self.stdout.write('')
                self.stdout.write(
                    self.style.SUCCESS('💾 Cambios guardados en la base de datos')
                )
            else:
                self.stdout.write('')
                self.stdout.write(
                    self.style.WARNING('🔍 Para ejecutar los cambios, ejecute sin --dry-run')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error durante el procesamiento: {str(e)}')
            )
            raise