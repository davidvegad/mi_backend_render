#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the sys.path
sys.path.append('/mnt/c/Users/davi_/Documents/Render/mi_api_backend')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Setup Django
django.setup()

from pacifik.models import Area

# Crear área de prueba
area = Area.objects.create(
    nombre='Salon de Fiestas',
    instrucciones='Mantener limpio despues del uso. Maximo 50 personas.',
    cupos_por_horario=1,
    horarios_permitidos={
        'lunes': ['18:00-22:00'],
        'martes': ['18:00-22:00'],
        'miercoles': ['18:00-22:00'],
        'jueves': ['18:00-22:00'],
        'viernes': ['18:00-22:00'],
        'sabado': ['14:00-22:00'],
        'domingo': ['14:00-22:00']
    },
    duraciones_permitidas=[4]
)

print(f'Area creada: {area.nombre}')

# Crear segunda área
area2 = Area.objects.create(
    nombre='Gimnasio',
    instrucciones='Usar solo zapatillas deportivas. Limpiar equipos despues del uso.',
    cupos_por_horario=3,
    horarios_permitidos={
        'lunes': ['06:00-08:00', '18:00-20:00'],
        'martes': ['06:00-08:00', '18:00-20:00'],
        'miercoles': ['06:00-08:00', '18:00-20:00'],
        'jueves': ['06:00-08:00', '18:00-20:00'],
        'viernes': ['06:00-08:00', '18:00-20:00'],
        'sabado': ['08:00-12:00', '14:00-18:00'],
        'domingo': ['08:00-12:00', '14:00-18:00']
    },
    duraciones_permitidas=[1, 2]
)

print(f'Area creada: {area2.nombre}')