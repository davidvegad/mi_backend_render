from django.core.management.base import BaseCommand
from pacifik.models import Area

class Command(BaseCommand):
    help = 'Inicializa las áreas comunes del edificio Pacifik Ocean Tower según especificaciones exactas'

    def handle(self, *args, **options):
        areas_data = [
            {
                "nombre": "Coworking",
                "instrucciones": "DISPOSICIONES ESPECIALES PARA EL USO DEL CO-WORKING: 1. Se permite uso simultáneo de personas de diferentes departamentos siempre que se respete el aforo de 11 personas; en este caso, no existe cobro de uso. 2. El espacio permanecerá cerrado, se pedirá la apertura con reserva y podrán solicitar control de aire acondicionado con cargo. 3. Se realizará la reserva hasta por 3 horas de forma exclusiva. 4. Si el propietario tiene invitados para uso exclusivo se tiene que hacer una reserva por el canal respectivo, donde se le indicará al resto de propietarios que en ese espacio de 3 horas estará reservado de forma exclusiva, el costo será de S/.30 soles. 5. Aforo 11 personas. 6. Horario de Lunes a domingo de 6am a 12am.",
                "cupos_por_horario": 4,
                "horarios_permitidos": {
                    "lunes": ["06:00-09:00", "09:00-12:00", "12:00-15:00", "15:00-18:00", "18:00-21:00", "21:00-23:59"],
                    "martes": ["06:00-09:00", "09:00-12:00", "12:00-15:00", "15:00-18:00", "18:00-21:00", "21:00-23:59"],
                    "miercoles": ["06:00-09:00", "09:00-12:00", "12:00-15:00", "15:00-18:00", "18:00-21:00", "21:00-23:59"],
                    "jueves": ["06:00-09:00", "09:00-12:00", "12:00-15:00", "15:00-18:00", "18:00-21:00", "21:00-23:59"],
                    "viernes": ["06:00-09:00", "09:00-12:00", "12:00-15:00", "15:00-18:00", "18:00-21:00", "21:00-23:59"],
                    "sabado": ["06:00-09:00", "09:00-12:00", "12:00-15:00", "15:00-18:00", "18:00-21:00", "21:00-23:59"],
                    "domingo": ["06:00-09:00", "09:00-12:00", "12:00-15:00", "15:00-18:00", "18:00-21:00", "21:00-23:59"]
                },
                "duraciones_permitidas": [3]
            },
            {
                "nombre": "Lounge",
                "instrucciones": "DISPOSICIONES ESPECIALES PARA EL USO DEL LOUNGE: 1. El espacio permanecerá cerrado y será reservado. 2. Existen dos tipos de reservas: a. Por turnos de 1 hora donde pueden ingresar varios usuarios a la vez respetando el aforo, no tiene costo y deberá velar por el buen uso y limpieza del espacio utilizado. b. Por exclusividad donde deberán abonar previamente una garantía de S/500, la cual será devuelta después de la correcta revisión del mobiliario como máximo 48 horas después del evento. 3. Para fechas especiales NO SE PUEDE RESERVAR: Día del padre, Día de la madre, 28 y 29 de julio, Halloween, Navidad, Año Nuevo. 4. La garantía será devuelta en su totalidad o parcialmente, según la revisión posterior del mobiliario. 5. En el espacio está prohibido fumar, con la salvedad de estar en la zona de terraza al tener una reserva en exclusividad. 6. Para la reserva exclusiva del lounge se dará prioridad a los cumpleaños de los propietarios y arrendatarios. 7. Aforo 40 personas. 8. El pago de la reserva se debe cancelar en un plazo no mayor de 72 horas.",
                "cupos_por_horario": 1,
                "horarios_permitidos": {
                    "lunes": ["09:00-13:00", "13:00-17:00", "17:00-21:00", "21:00-23:59"],
                    "martes": ["09:00-13:00", "13:00-17:00", "17:00-21:00", "21:00-23:59"],
                    "miercoles": ["09:00-13:00", "13:00-17:00", "17:00-21:00", "21:00-23:59"],
                    "jueves": ["09:00-13:00", "13:00-17:00", "17:00-21:00", "21:00-23:59"],
                    "viernes": ["09:00-13:00", "13:00-17:00", "17:00-21:00", "21:00-23:59"],
                    "sabado": ["09:00-13:00", "13:00-17:00", "17:00-21:00", "21:00-23:59"],
                    "domingo": ["09:00-13:00", "13:00-17:00", "17:00-21:00", "21:00-23:59"]
                },
                "duraciones_permitidas": [4]
            },
            {
                "nombre": "Cine",
                "instrucciones": "DISPOSICIONES ESPECIALES PARA EL USO DE LA SALA DE CINE: 1. El espacio permanecerá cerrado y solo utilizado bajo reserva. 2. La reserva es de forma exclusiva de espacios de hasta 3 horas, respetando el aforo máximo. 3. Se realizará un pago de S/30.00 para limpieza y fondo de mantenimiento por uso habitual. 4. Se puede consumir alimentos y/o bebidas buscando siempre el cuidado del mobiliario. 5. Se entregará al propietario los controles y se firmará el cargo correspondiente. 6. No está permitido fumar en esta área. 7. Para fechas especiales deportivas de gran magnitud son libres para los propietarios respetando el aforo. 8. Aforo 20 personas.",
                "cupos_por_horario": 1,
                "horarios_permitidos": {
                    "lunes": ["08:00-11:00", "11:00-14:00", "14:00-17:00", "17:00-20:00", "20:00-23:00"],
                    "martes": ["08:00-11:00", "11:00-14:00", "14:00-17:00", "17:00-20:00", "20:00-23:00"],
                    "miercoles": ["08:00-11:00", "11:00-14:00", "14:00-17:00", "17:00-20:00", "20:00-23:00"],
                    "jueves": ["08:00-11:00", "11:00-14:00", "14:00-17:00", "17:00-20:00", "20:00-23:00"],
                    "viernes": ["08:00-11:00", "11:00-14:00", "14:00-17:00", "17:00-20:00", "20:00-23:00"],
                    "sabado": ["08:00-11:00", "11:00-14:00", "14:00-17:00", "17:00-20:00", "20:00-23:00"],
                    "domingo": ["08:00-11:00", "11:00-14:00", "14:00-17:00", "17:00-20:00", "20:00-23:00"]
                },
                "duraciones_permitidas": [3]
            },
            {
                "nombre": "Juegos de salón",
                "instrucciones": "DISPOSICIONES ESPECIALES PARA EL USO DE LA SALA DE JUEGOS DE SALÓN: Este espacio es para niños y adultos. 1. El espacio permanecerá cerrado y será reservado por juego. 2. Niños menores de 12 años con la compañía de un adulto. 3. Cada residente podrá utilizar los equipos un máximo de 3 horas por reserva. 4. Para utilizar un equipo, el personal de vigilancia o conserje asignará un juego para su uso. 5. No está permitido el consumo de alimentos. Se permite llevar un tomatodo hermético solamente con agua o hidratante. 6. Por el momento no está permitido el ingreso de bebidas alcohólicas. 7. Está prohibido fumar en esta área. 8. De ocasionarse algún daño por el uso este deberá ser asumido por el residente responsable. 9. Se permitirán 3 invitados por reserva de lunes a domingo. 10. Si desea exclusividad el costo será de S/.50 soles por 3 horas. 11. Aforo 12 personas. Equipos: 2 Mesas de Ping pong, 1 Mesa de Billar, 1 Fulbito de mesa.",
                "cupos_por_horario": 3,
                "horarios_permitidos": {
                    "lunes": ["08:00-11:00", "11:00-14:00", "14:00-17:00", "17:00-20:00", "20:00-23:00"],
                    "martes": ["08:00-11:00", "11:00-14:00", "14:00-17:00", "17:00-20:00", "20:00-23:00"],
                    "miercoles": ["08:00-11:00", "11:00-14:00", "14:00-17:00", "17:00-20:00", "20:00-23:00"],
                    "jueves": ["08:00-11:00", "11:00-14:00", "14:00-17:00", "17:00-20:00", "20:00-23:00"],
                    "viernes": ["08:00-11:00", "11:00-14:00", "14:00-17:00", "17:00-20:00", "20:00-23:00"],
                    "sabado": ["08:00-11:00", "11:00-14:00", "14:00-17:00", "17:00-20:00", "20:00-23:00"],
                    "domingo": ["08:00-11:00", "11:00-14:00", "14:00-17:00", "17:00-20:00", "20:00-23:00"]
                },
                "duraciones_permitidas": [3]
            },
            {
                "nombre": "Gimnasio",
                "instrucciones": "DISPOSICIONES ESPECIALES PARA EL USO DEL GIMNASIO: 1. Puede ser utilizado solo por los residentes haciéndose responsables de cualquier daño que ocurra en su permanencia. 2. Se ingresa por medio de una reserva a través de la plataforma respectiva, esta será por equipo o material requerido. 3. Cada residente podrá utilizar el gimnasio un turno diario, el tiempo máximo de uso de cada turno no será mayor a 1 hora. 4. Los aparatos y máquinas serán usados con el debido cuidado. 5. No se podrá utilizar el gimnasio mojado o con ropa húmeda. 6. Los niños menores de 15 años solo ingresarán con compañía de un adulto. 7. Se encuentra prohibida la ingesta de alimentos en estas instalaciones. 8. Cada residente que use el gimnasio deberá de llevar obligatoriamente una toalla. 9. Está prohibido fumar e ingerir alcohol en esta área. 10. El uso de música deberá ser a un volumen prudente o se recomienda el uso de audífonos. 11. El vestuario a utilizar deberá ser deportivo. 12. Aforo 8 personas. Equipos: 2 Bicicletas estacionarias, 1 Elíptica, 2 Corredoras, 1 Gimnasio multifuncional, equipos de pesas, mats, sogas, ligas, cojines, bloques yoga.",
                "cupos_por_horario": 4,
                "horarios_permitidos": {
                    "lunes": ["06:00-07:00", "07:00-08:00", "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00", "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00", "17:00-18:00", "18:00-19:00", "19:00-20:00", "20:00-21:00", "21:00-22:00", "22:00-23:00", "23:00-23:59"],
                    "martes": ["06:00-07:00", "07:00-08:00", "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00", "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00", "17:00-18:00", "18:00-19:00", "19:00-20:00", "20:00-21:00", "21:00-22:00", "22:00-23:00", "23:00-23:59"],
                    "miercoles": ["06:00-07:00", "07:00-08:00", "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00", "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00", "17:00-18:00", "18:00-19:00", "19:00-20:00", "20:00-21:00", "21:00-22:00", "22:00-23:00", "23:00-23:59"],
                    "jueves": ["06:00-07:00", "07:00-08:00", "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00", "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00", "17:00-18:00", "18:00-19:00", "19:00-20:00", "20:00-21:00", "21:00-22:00", "22:00-23:00", "23:00-23:59"],
                    "viernes": ["06:00-07:00", "07:00-08:00", "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00", "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00", "17:00-18:00", "18:00-19:00", "19:00-20:00", "20:00-21:00", "21:00-22:00", "22:00-23:00", "23:00-23:59"],
                    "sabado": ["06:00-07:00", "07:00-08:00", "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00", "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00", "17:00-18:00", "18:00-19:00", "19:00-20:00", "20:00-21:00", "21:00-22:00", "22:00-23:00", "23:00-23:59"],
                    "domingo": ["06:00-07:00", "07:00-08:00", "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00", "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00", "17:00-18:00", "18:00-19:00", "19:00-20:00", "20:00-21:00", "21:00-22:00", "22:00-23:00", "23:00-23:59"]
                },
                "duraciones_permitidas": [1]
            },
            {
                "nombre": "Sauna",
                "instrucciones": "DISPOSICIONES ESPECIALES PARA EL USO DEL SAUNA: 1. El espacio permanecerá cerrado. 2. Puede ser utilizado solo por los residentes e invitados junto con el residente responsable respetando el aforo. 3. Solo se permite una reserva por turno. 4. La reserva tiene un espacio máximo de 1 hora. 5. No está permitido el uso de elementos de ningún tipo sobre la bandeja que emana calor, por precaución. 6. No está permitido el ingreso de bebidas o alimentos, solo de tomatodos debidamente cerrados con agua. 7. No podrán ingresar en ropa interior o desnudos a dicha área. 8. El residente es responsable por el correcto uso de los equipos, donde será capacitado previamente a su uso. 9. No está permitido ingreso a menores de 12 años. 10. No está permitido fumar en el área.",
                "cupos_por_horario": 1,
                "horarios_permitidos": {
                    "lunes": ["06:00-07:00", "07:00-08:00", "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00", "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00", "17:00-18:00", "18:00-19:00", "19:00-20:00", "20:00-21:00", "21:00-22:00", "22:00-23:00", "23:00-23:59"],
                    "martes": ["06:00-07:00", "07:00-08:00", "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00", "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00", "17:00-18:00", "18:00-19:00", "19:00-20:00", "20:00-21:00", "21:00-22:00", "22:00-23:00", "23:00-23:59"],
                    "miercoles": ["06:00-07:00", "07:00-08:00", "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00", "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00", "17:00-18:00", "18:00-19:00", "19:00-20:00", "20:00-21:00", "21:00-22:00", "22:00-23:00", "23:00-23:59"],
                    "jueves": ["06:00-07:00", "07:00-08:00", "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00", "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00", "17:00-18:00", "18:00-19:00", "19:00-20:00", "20:00-21:00", "21:00-22:00", "22:00-23:00", "23:00-23:59"],
                    "viernes": ["06:00-07:00", "07:00-08:00", "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00", "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00", "17:00-18:00", "18:00-19:00", "19:00-20:00", "20:00-21:00", "21:00-22:00", "22:00-23:00", "23:00-23:59"],
                    "sabado": ["06:00-07:00", "07:00-08:00", "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00", "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00", "17:00-18:00", "18:00-19:00", "19:00-20:00", "20:00-21:00", "21:00-22:00", "22:00-23:00", "23:00-23:59"],
                    "domingo": ["06:00-07:00", "07:00-08:00", "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00", "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00", "17:00-18:00", "18:00-19:00", "19:00-20:00", "20:00-21:00", "21:00-22:00", "22:00-23:00", "23:00-23:59"]
                },
                "duraciones_permitidas": [1]
            },
            {
                "nombre": "Piscina",
                "instrucciones": "DISPOSICIONES ESPECIALES PARA EL USO DE LAS PISCINAS (DE ADULTOS Y DE NIÑOS): 1. El uso de la piscina y las medidas de seguridad son de exclusiva responsabilidad de los Titulares. Tratándose de menores de edad, éstos deberán encontrarse bajo la supervisión permanente de un adulto. 2. Antes del ingreso a la piscina, los Titulares o usuarios deberán ducharse en los SS.HH destinados para dicho fin. 3. Está prohibido llevar objetos de vidrio, metales u otros que pudieran causar accidentes. Prohibido el consumo de bebidas alcohólicas y comer en el área de la piscina. 4. Queda prohibido Fumar en este ambiente. 5. De Lunes a Viernes se permitirán tres invitados por departamento. Sábado y domingo será de uso exclusivo para los propietarios y residentes siempre respetando el aforo señalado. 6. No se permite el uso de la piscina a niños menores de 12 años sin la compañía de un adulto responsable. 7. Los días lunes y viernes se procederá al mantenimiento de las piscinas, las reservas serán a partir del medio día (12:00 pm). 8. No se permite el ingreso de personas en estado de ebriedad. 9. La piscina puede ser reservada a través del canal de reservas por un espacio máximo de 3 horas, respetando los aforos totales. 10. Aforo máximo según reservas simultáneas.",
                "cupos_por_horario": 8,
                "horarios_permitidos": {
                    "lunes": ["12:00-15:00", "15:00-18:00", "18:00-21:00", "21:00-23:59"],
                    "martes": ["06:00-09:00", "09:00-12:00", "12:00-15:00", "15:00-18:00", "18:00-21:00", "21:00-23:59"],
                    "miercoles": ["06:00-09:00", "09:00-12:00", "12:00-15:00", "15:00-18:00", "18:00-21:00", "21:00-23:59"],
                    "jueves": ["06:00-09:00", "09:00-12:00", "12:00-15:00", "15:00-18:00", "18:00-21:00", "21:00-23:59"],
                    "viernes": ["12:00-15:00", "15:00-18:00", "18:00-21:00", "21:00-23:59"],
                    "sabado": ["06:00-09:00", "09:00-12:00", "12:00-15:00", "15:00-18:00", "18:00-21:00", "21:00-23:59"],
                    "domingo": ["06:00-09:00", "09:00-12:00", "12:00-15:00", "15:00-18:00", "18:00-21:00", "21:00-23:59"]
                },
                "duraciones_permitidas": [3]
            },
            {
                "nombre": "Parrilla",
                "instrucciones": "DISPOSICIONES ESPECIALES PARA EL USO DE LA ZONA DE PARRILLAS: 1. El uso de las parrillas tendrá un costo de S/50 soles para limpieza de parrilla y para mantenimientos futuros deterioro de uso normal. 2. Actualmente se podrá disponer de 2 parrillas por turno y 2 reservas de hasta 8 personas cada una. 3. El uso, cuidado y comportamiento de los invitados es responsabilidad absoluta del propietario que realiza la reserva. 4. Los usuarios son los responsables por la limpieza y cuidados de los equipos y ambientes comunes utilizados excepto las parrillas que serán limpiadas por personal idóneo. 5. Se permite el uso de pequeños parlantes de música siempre y cuando el volumen sea prudente y no perturbe la tranquilidad de alguna reserva contigua. 6. Se prohíbe fumar en este espacio, en caso sea una reserva única pueden realizarlo siempre y cuando utilicen cenicero y no arrojar colillas por la ventana, en el piso, asientos, macetas, etc.",
                "cupos_por_horario": 2,
                "horarios_permitidos": {
                    "lunes": ["11:00-17:00", "18:00-23:45"],
                    "martes": ["11:00-17:00", "18:00-23:45"],
                    "miercoles": ["11:00-17:00", "18:00-23:45"],
                    "jueves": ["11:00-17:00", "18:00-23:45"],
                    "viernes": ["11:00-17:00", "18:00-23:45"],
                    "sabado": ["11:00-17:00", "18:00-23:45"],
                    "domingo": ["11:00-17:00", "18:00-23:45"]
                },
                "duraciones_permitidas": [6]
            }
        ]

        self.stdout.write('Inicializando áreas comunes según especificaciones exactas...')
        
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