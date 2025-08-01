from django.core.management.base import BaseCommand
from pacifik.models import Area

class Command(BaseCommand):
    help = 'Inicializa las áreas comunes del edificio Pacifik Ocean Tower'

    def handle(self, *args, **options):
        areas_data = [
            {
                "nombre": "Piscina",
                "instrucciones": "Uso exclusivo para residentes. Horario de 6:00 AM a 10:00 PM. Máximo 8 personas simultáneamente. Niños deben estar acompañados por adultos. Prohibido introducir vidrio o alimentos.",
                "cupos_por_horario": 8,
                "horarios_permitidos": {
                    "lunes": ["06:00-08:00", "08:00-10:00", "10:00-12:00", "14:00-16:00", "16:00-18:00", "18:00-20:00", "20:00-22:00"],
                    "martes": ["06:00-08:00", "08:00-10:00", "10:00-12:00", "14:00-16:00", "16:00-18:00", "18:00-20:00", "20:00-22:00"],
                    "miercoles": ["06:00-08:00", "08:00-10:00", "10:00-12:00", "14:00-16:00", "16:00-18:00", "18:00-20:00", "20:00-22:00"],
                    "jueves": ["06:00-08:00", "08:00-10:00", "10:00-12:00", "14:00-16:00", "16:00-18:00", "18:00-20:00", "20:00-22:00"],
                    "viernes": ["06:00-08:00", "08:00-10:00", "10:00-12:00", "14:00-16:00", "16:00-18:00", "18:00-20:00", "20:00-22:00"],
                    "sabado": ["08:00-10:00", "10:00-12:00", "14:00-16:00", "16:00-18:00", "18:00-20:00", "20:00-22:00"],
                    "domingo": ["08:00-10:00", "10:00-12:00", "14:00-16:00", "16:00-18:00", "18:00-20:00", "20:00-22:00"]
                },
                "duraciones_permitidas": [2, 3, 4]
            },
            {
                "nombre": "Gimnasio",
                "instrucciones": "Uso exclusivo para residentes. Disponible 24/7. Máximo 6 personas simultáneamente. Obligatorio el uso de toalla. Limpiar equipos después del uso. Prohibido hacer ruido excesivo después de las 10:00 PM.",
                "cupos_por_horario": 6,
                "horarios_permitidos": {
                    "lunes": ["05:00-07:00", "07:00-09:00", "09:00-11:00", "11:00-13:00", "13:00-15:00", "15:00-17:00", "17:00-19:00", "19:00-21:00", "21:00-23:00"],
                    "martes": ["05:00-07:00", "07:00-09:00", "09:00-11:00", "11:00-13:00", "13:00-15:00", "15:00-17:00", "17:00-19:00", "19:00-21:00", "21:00-23:00"],
                    "miercoles": ["05:00-07:00", "07:00-09:00", "09:00-11:00", "11:00-13:00", "13:00-15:00", "15:00-17:00", "17:00-19:00", "19:00-21:00", "21:00-23:00"],
                    "jueves": ["05:00-07:00", "07:00-09:00", "09:00-11:00", "11:00-13:00", "13:00-15:00", "15:00-17:00", "17:00-19:00", "19:00-21:00", "21:00-23:00"],
                    "viernes": ["05:00-07:00", "07:00-09:00", "09:00-11:00", "11:00-13:00", "13:00-15:00", "15:00-17:00", "17:00-19:00", "19:00-21:00", "21:00-23:00"],
                    "sabado": ["06:00-08:00", "08:00-10:00", "10:00-12:00", "12:00-14:00", "14:00-16:00", "16:00-18:00", "18:00-20:00", "20:00-22:00"],
                    "domingo": ["06:00-08:00", "08:00-10:00", "10:00-12:00", "12:00-14:00", "14:00-16:00", "16:00-18:00", "18:00-20:00", "20:00-22:00"]
                },
                "duraciones_permitidas": [1, 2]
            },
            {
                "nombre": "Salón de Eventos",
                "instrucciones": "Reserva con 48 horas de anticipación. Máximo 25 personas. Incluye mesas, sillas y sistema de sonido básico. Debe dejarse limpio después del uso. Prohibido fumar. Horario hasta las 11:00 PM entre semana y hasta las 12:00 AM los fines de semana.",
                "cupos_por_horario": 1,
                "horarios_permitidos": {
                    "lunes": ["10:00-14:00", "14:00-18:00", "18:00-23:00"],
                    "martes": ["10:00-14:00", "14:00-18:00", "18:00-23:00"],
                    "miercoles": ["10:00-14:00", "14:00-18:00", "18:00-23:00"],
                    "jueves": ["10:00-14:00", "14:00-18:00", "18:00-23:00"],
                    "viernes": ["10:00-14:00", "14:00-18:00", "18:00-24:00"],
                    "sabado": ["10:00-14:00", "14:00-18:00", "18:00-24:00"],
                    "domingo": ["10:00-14:00", "14:00-18:00", "18:00-23:00"]
                },
                "duraciones_permitidas": [4, 6, 8]
            },
            {
                "nombre": "Terraza BBQ",
                "instrucciones": "Área para asados familiares. Incluye 2 parrillas de gas y área de mesas. Máximo 20 personas. Debe reservarse con 24 horas de anticipación. Limpieza obligatoria después del uso. Prohibido después de las 10:00 PM por ruido.",
                "cupos_por_horario": 1,
                "horarios_permitidos": {
                    "lunes": [],
                    "martes": [],
                    "miercoles": [],
                    "jueves": [],
                    "viernes": ["12:00-16:00", "16:00-20:00", "20:00-22:00"],
                    "sabado": ["10:00-14:00", "14:00-18:00", "18:00-22:00"],
                    "domingo": ["10:00-14:00", "14:00-18:00", "18:00-22:00"]
                },
                "duraciones_permitidas": [4, 6]
            },
            {
                "nombre": "Business Center",
                "instrucciones": "Espacio de trabajo compartido con internet de alta velocidad, impresora y sala de reuniones. Máximo 8 personas. Silencio obligatorio. Disponible 24/7. Ideal para trabajo remoto y reuniones profesionales.",
                "cupos_por_horario": 8,
                "horarios_permitidos": {
                    "lunes": ["06:00-10:00", "10:00-14:00", "14:00-18:00", "18:00-22:00"],
                    "martes": ["06:00-10:00", "10:00-14:00", "14:00-18:00", "18:00-22:00"],
                    "miercoles": ["06:00-10:00", "10:00-14:00", "14:00-18:00", "18:00-22:00"],
                    "jueves": ["06:00-10:00", "10:00-14:00", "14:00-18:00", "18:00-22:00"],
                    "viernes": ["06:00-10:00", "10:00-14:00", "14:00-18:00", "18:00-22:00"],
                    "sabado": ["08:00-12:00", "12:00-16:00", "16:00-20:00"],
                    "domingo": ["08:00-12:00", "12:00-16:00", "16:00-20:00"]
                },
                "duraciones_permitidas": [2, 4, 6]
            },
            {
                "nombre": "Cancha de Tenis",
                "instrucciones": "Cancha reglamentaria con iluminación LED. Máximo 4 personas por reserva (dobles). Obligatorio el uso de calzado deportivo adecuado. Reservas de máximo 2 horas. Incluye red y postes. Raquetas y pelotas por cuenta del usuario.",
                "cupos_por_horario": 4,
                "horarios_permitidos": {
                    "lunes": ["06:00-08:00", "08:00-10:00", "10:00-12:00", "14:00-16:00", "16:00-18:00", "18:00-20:00", "20:00-22:00"],
                    "martes": ["06:00-08:00", "08:00-10:00", "10:00-12:00", "14:00-16:00", "16:00-18:00", "18:00-20:00", "20:00-22:00"],
                    "miercoles": ["06:00-08:00", "08:00-10:00", "10:00-12:00", "14:00-16:00", "16:00-18:00", "18:00-20:00", "20:00-22:00"],
                    "jueves": ["06:00-08:00", "08:00-10:00", "10:00-12:00", "14:00-16:00", "16:00-18:00", "18:00-20:00", "20:00-22:00"],
                    "viernes": ["06:00-08:00", "08:00-10:00", "10:00-12:00", "14:00-16:00", "16:00-18:00", "18:00-20:00", "20:00-22:00"],
                    "sabado": ["07:00-09:00", "09:00-11:00", "11:00-13:00", "15:00-17:00", "17:00-19:00", "19:00-21:00"],
                    "domingo": ["07:00-09:00", "09:00-11:00", "11:00-13:00", "15:00-17:00", "17:00-19:00", "19:00-21:00"]
                },
                "duraciones_permitidas": [1, 2]
            }
        ]

        self.stdout.write('Inicializando áreas comunes...')
        
        created_count = 0
        updated_count = 0
        
        for area_data in areas_data:
            area, created = Area.objects.get_or_create(
                nombre=area_data["nombre"],
                defaults=area_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Área creada: {area.nombre}')
                )
            else:
                # Actualizar área existente
                for key, value in area_data.items():
                    setattr(area, key, value)
                area.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Área actualizada: {area.nombre}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Proceso completado:\n'
                f'- {created_count} áreas creadas\n'
                f'- {updated_count} áreas actualizadas\n'
                f'- Total áreas: {Area.objects.count()}'
            )
        )