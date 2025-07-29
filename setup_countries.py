#!/usr/bin/env python
"""
Script para configurar países por defecto en TimeHub
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from timehub.models import Country, Holiday
from datetime import date

def create_default_countries():
    """Crear países por defecto con configuraciones"""
    
    # Perú
    peru, created = Country.objects.get_or_create(
        code='PER',
        defaults={
            'name': 'Perú',
            'annual_vacation_days': 30,
            'work_days': [1, 2, 3, 4, 5],  # Lun-Vie
            'timezone': 'America/Lima',
            'max_maternity_days': 98,  # Ley peruana
            'max_paternity_days': 10,  # Ley peruana
            'max_sick_days': 60,       # Puede extenderse con certificado médico
            'max_bereavement_days': 3,
            'max_personal_days': 5,
            'is_active': True
        }
    )
    
    if created:
        print(f"País creado: {peru.name}")
        
        # Feriados de Perú 2025
        holidays_2025 = [
            ('Año Nuevo', date(2025, 1, 1)),
            ('Viernes Santo', date(2025, 4, 18)),
            ('Día del Trabajo', date(2025, 5, 1)),
            ('Día de la Independencia', date(2025, 7, 28)),
            ('Día de la Independencia', date(2025, 7, 29)),
            ('Santa Rosa de Lima', date(2025, 8, 30)),
            ('Combate de Angamos', date(2025, 10, 8)),
            ('Todos los Santos', date(2025, 11, 1)),
            ('Inmaculada Concepción', date(2025, 12, 8)),
            ('Navidad', date(2025, 12, 25)),
        ]
        
        for name, holiday_date in holidays_2025:
            Holiday.objects.get_or_create(
                country=peru,
                name=name,
                date=holiday_date,
                defaults={'is_recurring': True}
            )
        
        print(f"Feriados de Perú 2025 creados: {len(holidays_2025)}")
    
    # Estados Unidos
    usa, created = Country.objects.get_or_create(
        code='USA',
        defaults={
            'name': 'Estados Unidos',
            'annual_vacation_days': 15,  # Promedio en USA
            'work_days': [1, 2, 3, 4, 5],  # Lun-Vie
            'timezone': 'America/New_York',
            'max_maternity_days': 84,  # 12 semanas FMLA
            'max_paternity_days': 84,  # 12 semanas FMLA
            'max_sick_days': 40,       # Promedio empresarial
            'max_bereavement_days': 5,
            'max_personal_days': 10,
            'is_active': True
        }
    )
    
    if created:
        print(f"País creado: {usa.name}")
    
    # España
    spain, created = Country.objects.get_or_create(
        code='ESP',
        defaults={
            'name': 'España',
            'annual_vacation_days': 22,  # Mínimo legal en España
            'work_days': [1, 2, 3, 4, 5],  # Lun-Vie
            'timezone': 'Europe/Madrid',
            'max_maternity_days': 112,  # 16 semanas
            'max_paternity_days': 112,  # 16 semanas
            'max_sick_days': 365,       # Puede extenderse hasta 1 año
            'max_bereavement_days': 2,
            'max_personal_days': 6,
            'is_active': True
        }
    )
    
    if created:
        print(f"País creado: {spain.name}")
    
    # México
    mexico, created = Country.objects.get_or_create(
        code='MEX',
        defaults={
            'name': 'México',
            'annual_vacation_days': 12,  # Mínimo legal en México
            'work_days': [1, 2, 3, 4, 5],  # Lun-Vie
            'timezone': 'America/Mexico_City',
            'max_maternity_days': 84,   # 12 semanas
            'max_paternity_days': 5,    # 5 días
            'max_sick_days': 52,        # Hasta 52 semanas con IMSS
            'max_bereavement_days': 1,
            'max_personal_days': 3,
            'is_active': True
        }
    )
    
    if created:
        print(f"País creado: {mexico.name}")

def create_default_leave_types():
    """Crear tipos de permiso por defecto"""
    from timehub.models import LeaveType
    
    leave_types = [
        {
            'name': 'Vacaciones Anuales',
            'code': 'VACATION',
            'is_paid': True,
            'deducts_from_balance': True,
            'requires_attachment': False,
            'max_days_per_request': 15,
            'is_active': True
        },
        {
            'name': 'Licencia por Maternidad',
            'code': 'MATERNITY',
            'is_paid': True,
            'deducts_from_balance': False,
            'requires_attachment': True,
            'max_days_per_request': 98,  # Perú: 98 días
            'is_active': True
        },
        {
            'name': 'Licencia por Paternidad',
            'code': 'PATERNITY',
            'is_paid': True,
            'deducts_from_balance': False,
            'requires_attachment': True,
            'max_days_per_request': 10,  # Perú: 10 días
            'is_active': True
        },
        {
            'name': 'Permiso por Enfermedad',
            'code': 'SICK',
            'is_paid': True,
            'deducts_from_balance': False,
            'requires_attachment': True,
            'max_days_per_request': 30,
            'is_active': True
        },
        {
            'name': 'Permiso Personal',
            'code': 'PERSONAL',
            'is_paid': False,
            'deducts_from_balance': False,
            'requires_attachment': False,
            'max_days_per_request': 5,
            'is_active': True
        },
        {
            'name': 'Permiso por Luto',
            'code': 'BEREAVEMENT',
            'is_paid': True,
            'deducts_from_balance': False,
            'requires_attachment': True,
            'max_days_per_request': 3,
            'is_active': True
        }
    ]
    
    for leave_type_data in leave_types:
        leave_type, created = LeaveType.objects.get_or_create(
            name=leave_type_data['name'],
            defaults=leave_type_data
        )
        if created:
            print(f"Tipo de permiso creado: {leave_type.name}")

def main():
    print("Configurando datos por defecto para TimeHub...")
    print()
    
    print("Creando países...")
    create_default_countries()
    print()
    
    print("Creando tipos de permiso...")
    create_default_leave_types()
    print()
    
    print("Configuración completada!")
    print()
    print("Próximos pasos:")
    print("1. Asignar países a los usuarios en UserProfile")
    print("2. Configurar balance inicial de vacaciones por usuario")
    print("3. Ejecutar migraciones si es necesario:")
    print("   python manage.py makemigrations")
    print("   python manage.py migrate")

if __name__ == '__main__':
    main()