from django.core.management.base import BaseCommand
from django.utils import timezone
from pacifik.models import Reserva
from datetime import timedelta


class Command(BaseCommand):
    help = 'Marca como completadas las reservas del día anterior automáticamente'

    def handle(self, *args, **options):
        # TEMPORAL: Obtener la fecha de HOY para pruebas
        # En producción cambiar a: timezone.now().date() - timedelta(days=1)
        hoy = timezone.now().date()
        
        # Buscar reservas de HOY que estén en estado 'reservado'
        reservas_a_completar = Reserva.objects.filter(
            fecha=hoy,
            estado='reservado'
        )
        
        # Contar cuántas se van a actualizar
        count = reservas_a_completar.count()
        
        if count > 0:
            # Actualizar a completado
            reservas_a_completar.update(estado='completado')
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ PRUEBA: Se completaron automáticamente {count} reservas del {hoy.strftime("%d/%m/%Y")} (HOY)'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'ℹ️  No hay reservas pendientes para completar del {hoy.strftime("%d/%m/%Y")} (HOY)'
                )
            )
        
        return f"Comando ejecutado exitosamente. {count} reservas completadas de HOY."