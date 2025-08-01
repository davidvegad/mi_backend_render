#!/usr/bin/env python
"""
Script para verificar que el endpoint de reservas funciona correctamente
"""

import os
import sys
import django
import json

# Configurar Django
sys.path.append('/mnt/c/Users/davi_/Documents/Render/mi_api_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

try:
    django.setup()
    print("✅ Django configurado correctamente")
except Exception as e:
    print(f"❌ Error configurando Django: {e}")
    sys.exit(1)

from pacifik.models import Reserva, UserProfile
from pacifik.serializers import ReservaListSerializer
from django.contrib.auth.models import User

def test_models():
    """Test básico de modelos"""
    print("\n🔍 TESTING MODELOS:")
    
    # Test reservas
    total_reservas = Reserva.objects.count()
    print(f"📊 Total reservas: {total_reservas}")
    
    if total_reservas == 0:
        print("⚠️  No hay reservas en la base de datos")
        return False
    
    # Test usuarios y profiles
    users = User.objects.all()[:3]
    print(f"👥 Usuarios en DB: {User.objects.count()}")
    
    for user in users:
        print(f"   - Usuario {user.id}: {user.get_full_name()}")
        try:
            profile = user.userprofile
            print(f"     ✅ Profile: Depto {profile.numero_departamento}")
        except UserProfile.DoesNotExist:
            print(f"     ❌ Sin UserProfile")
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
    return True

def test_serializer():
    """Test del serializer"""
    print("\n🔍 TESTING SERIALIZER:")
    
    reservas = Reserva.objects.all()[:3]
    
    for reserva in reservas:
        print(f"   - Reserva {reserva.id}:")
        try:
            serializer = ReservaListSerializer(reserva)
            data = serializer.data
            print(f"     ✅ Usuario: {data['usuario_nombre']}")
            print(f"     ✅ Departamento: {data['usuario_departamento']}")
            print(f"     ✅ Área: {data['area_nombre']}")
        except Exception as e:
            print(f"     ❌ Error serializer: {e}")

def test_query_filters():
    """Test de filtros de query"""
    print("\n🔍 TESTING FILTROS:")
    
    # Test query básica
    try:
        reservas = Reserva.objects.select_related('usuario', 'area', 'usuario__userprofile').all()
        print(f"   ✅ Query básica: {reservas.count()} reservas")
    except Exception as e:
        print(f"   ❌ Error query básica: {e}")
        return False
    
    # Test filtros específicos
    test_filters = [
        ('area vacía', {'area_id': ''}),
        ('fecha vacía', {'fecha': ''}),
        ('estado vacío', {'estado': ''}),
        ('departamento vacío', {'departamento': ''})
    ]
    
    for nombre, filtros in test_filters:
        try:
            query = reservas
            for key, value in filtros.items():
                if key == 'area_id' and value and value.strip():
                    query = query.filter(area_id=value)
                elif key == 'fecha' and value and value.strip():
                    query = query.filter(fecha=value)
                elif key == 'estado' and value and value.strip():
                    query = query.filter(estado=value)
                elif key == 'departamento' and value and value.strip():
                    query = query.filter(usuario__userprofile__numero_departamento__icontains=value)
            
            result = query.count()
            print(f"   ✅ {nombre}: {result} resultados")
        except Exception as e:
            print(f"   ❌ Error {nombre}: {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 INICIANDO TESTS DEL ENDPOINT DE RESERVAS")
    print("=" * 50)
    
    success = True
    
    try:
        success &= test_models()
        success &= test_serializer()
        success &= test_query_filters()
        
        if success:
            print("\n🎉 TODOS LOS TESTS PASARON")
            print("✅ El endpoint debería funcionar correctamente")
        else:
            print("\n❌ ALGUNOS TESTS FALLARON")
            print("⚠️  Revisar los errores arriba")
            
    except Exception as e:
        print(f"\n💥 ERROR GENERAL: {e}")
        sys.exit(1)