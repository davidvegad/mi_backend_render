from django.core.management.base import BaseCommand
from django.utils import timezone
from pacifik.models import Reserva
from datetime import timedelta


class Command(BaseCommand):
    help = 'Marca como completadas las reservas del día anterior automáticamente'

    def handle(self, *args, **options):
        # Obtener la fecha de ayer
        ayer = timezone.now().date() - timedelta(days=1)
        
        # Buscar reservas del día anterior que estén en estado 'reservado'
        reservas_a_completar = Reserva.objects.filter(
            fecha=ayer,
            estado='reservado'
        )
        
        # Contar cuántas se van a actualizar
        count = reservas_a_completar.count()
        
        if count > 0:
            # Actualizar a completado
            reservas_a_completar.update(estado='completado')
            self.stdout.write(
                self.style.SUCCESS(
                    f'Se completaron automáticamente {count} reservas del {ayer.strftime("%d/%m/%Y")}'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'No hay reservas pendientes para completar del {ayer.strftime("%d/%m/%Y")}'
                )
            )
        
        return f"Comando ejecutado exitosamente. {count} reservas completadas."