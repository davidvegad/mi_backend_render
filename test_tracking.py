#!/usr/bin/env python
"""
Script para testear el tracking de clicks en tiempo real
Ejecutar con: python manage.py shell < test_tracking.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from links.models import Profile, Link, ProfileView, LinkClick

def test_tracking():
    print("🔍 TESTING TRACKING DE CLICKS EN TIEMPO REAL")
    print("=" * 50)
    
    # Buscar el primer perfil
    profile = Profile.objects.first()
    if not profile:
        print("❌ No se encontró ningún perfil.")
        return
    
    links = list(profile.links.all())
    if not links:
        print("❌ No se encontraron enlaces en el perfil.")
        return
    
    print(f"✅ Perfil: {profile.name} ({profile.slug})")
    print(f"✅ Enlaces encontrados: {len(links)}")
    
    # Mostrar estado inicial
    print("\n📊 ESTADO INICIAL:")
    print(f"   👁️ Vistas del perfil: {profile.views}")
    print(f"   📈 Vistas detalladas: {ProfileView.objects.filter(profile=profile).count()}")
    
    total_clicks_legacy = sum(link.clicks for link in links)
    total_clicks_detailed = LinkClick.objects.filter(profile=profile).count()
    
    print(f"   🔗 Clicks legacy: {total_clicks_legacy}")
    print(f"   📈 Clicks detallados: {total_clicks_detailed}")
    
    print("\n📋 CLICKS POR ENLACE:")
    for link in links:
        detailed_clicks = LinkClick.objects.filter(link=link).count()
        print(f"   • {link.title}: {link.clicks} legacy / {detailed_clicks} detallados")
    
    print("\n" + "=" * 50)
    print("🔗 URLs PARA TESTING:")
    print(f"   👤 Perfil público: http://localhost:3000/{profile.slug}")
    print("   🎯 Haz click en los enlaces del perfil y luego ejecuta este script otra vez")
    
    print("\n📱 ENDPOINTS DE TRACKING:")
    for link in links:
        print(f"   • {link.title}: http://localhost:8000/api/linkinbio/link-clicks/{link.id}/")
    
    print(f"\n   📊 Vista perfil: http://localhost:8000/api/linkinbio/profile-views/{profile.slug}/")
    
    print("\n" + "=" * 50)
    print("🛠️ COMANDOS ÚTILES:")
    print("   • Ver admin: http://localhost:8000/admin/")
    print("   • Ejecutar otra vez: python manage.py shell < test_tracking.py")
    print("   • Ver logs: python manage.py runserver --verbosity=2")

if __name__ == "__main__":
    test_tracking()