#!/usr/bin/env python
"""
Script para simular el completado automático de reservas
Útil para testing y desarrollo
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
sys.path.append('/mnt/c/Users/davi_/Documents/Render/mi_api_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from pacifik.models import Reserva
from django.utils import timezone

def completar_reservas_simulacion():
    """Simula el completado automático de reservas"""
    
    print("🚀 Iniciando simulación de completado automático...")
    print(f"📅 Fecha actual: {timezone.now().date()}")
    
    # Obtener fecha de ayer para simular
    ayer = timezone.now().date() - timedelta(days=1)
    print(f"📅 Buscando reservas del: {ayer}")
    
    # Buscar reservas a completar
    reservas_a_completar = Reserva.objects.filter(
        fecha=ayer,
        estado='reservado'
    )
    
    total = reservas_a_completar.count()
    print(f"📊 Reservas encontradas: {total}")
    
    if total == 0:
        print("✅ No hay reservas pendientes para completar")
        
        # Mostrar todas las reservas para contexto
        todas_reservas = Reserva.objects.all().order_by('-fecha')[:10]
        if todas_reservas.exists():
            print("\n📋 Últimas 10 reservas en el sistema:")
            for reserva in todas_reservas:
                print(f"   - {reserva.usuario.get_full_name()} | {reserva.area.nombre} | {reserva.fecha} | {reserva.estado}")
        
        return
    
    # Mostrar reservas que se van a completar
    print(f"\n📋 Reservas que se completarán:")
    for reserva in reservas_a_completar:
        print(f"   - {reserva.usuario.get_full_name()} | {reserva.area.nombre} | {reserva.fecha} {reserva.horario_inicio}-{reserva.horario_fin}")
    
    # Confirmar acción
    respuesta = input(f"\n❓ ¿Completar {total} reserva(s)? (s/N): ").lower()
    
    if respuesta in ['s', 'si', 'y', 'yes']:
        # Completar reservas
        reservas_completadas = reservas_a_completar.update(estado='completado')
        print(f"✅ {reservas_completadas} reservas completadas exitosamente")
        
        # Mostrar resultado
        print(f"\n🎉 Proceso completado:")
        print(f"   - Reservas procesadas: {reservas_completadas}")
        print(f"   - Fecha procesada: {ayer}")
        print(f"   - Estado cambiado a: completado")
        
    else:
        print("❌ Operación cancelada")

def mostrar_estadisticas():
    """Muestra estadísticas de reservas"""
    print("\n📊 ESTADÍSTICAS DE RESERVAS:")
    
    total = Reserva.objects.count()
    reservadas = Reserva.objects.filter(estado='reservado').count()
    completadas = Reserva.objects.filter(estado='completado').count()
    canceladas = Reserva.objects.filter(estado='cancelado').count()
    
    print(f"   📋 Total: {total}")
    print(f"   🟢 Reservadas: {reservadas}")
    print(f"   ✅ Completadas: {completadas}")
    print(f"   ❌ Canceladas: {canceladas}")

if __name__ == "__main__":
    print("=" * 50)
    print("🏢 SIMULADOR DE COMPLETADO AUTOMÁTICO")
    print("=" * 50)
    
    try:
        mostrar_estadisticas()
        completar_reservas_simulacion()
        print("\n" + "=" * 50)
        mostrar_estadisticas()
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)