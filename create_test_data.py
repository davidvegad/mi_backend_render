#!/usr/bin/env python
"""
Script para crear datos de prueba para el sistema de analytics
Ejecutar con: python manage.py shell < create_test_data.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from links.models import Profile, Link, ProfileView, LinkClick
from django.contrib.auth.models import User

def create_test_data():
    print("🚀 Creando datos de prueba para analytics...")
    
    # Buscar el primer usuario y perfil
    try:
        user = User.objects.first()
        if not user:
            print("❌ No se encontró ningún usuario. Crea un usuario primero.")
            return
        
        profile = Profile.objects.filter(user=user).first()
        if not profile:
            print("❌ No se encontró perfil para el usuario. Crea un perfil primero.")
            return
            
        print(f"✅ Usando perfil: {profile.name} ({profile.slug})")
        
        # Verificar que hay enlaces
        links = list(profile.links.all())
        if not links:
            print("⚠️ No hay enlaces en el perfil. Creando enlaces de prueba...")
            # Crear enlaces de prueba
            link_data = [
                {"title": "Mi Instagram", "url": "https://instagram.com/user", "type": "instagram"},
                {"title": "Mi YouTube", "url": "https://youtube.com/user", "type": "youtube"},
                {"title": "WhatsApp", "url": "https://wa.me/1234567890", "type": "whatsapp"},
                {"title": "Mi Sitio Web", "url": "https://misitio.com", "type": "generic"},
                {"title": "TikTok", "url": "https://tiktok.com/@user", "type": "tiktok"},
            ]
            
            for i, data in enumerate(link_data):
                link = Link.objects.create(
                    profile=profile,
                    title=data["title"],
                    url=data["url"],
                    type=data["type"],
                    order=i
                )
                links.append(link)
            
            print(f"✅ Creados {len(links)} enlaces de prueba")
        
        # Crear vistas de perfil (últimos 30 días)
        print("📊 Creando vistas de perfil...")
        countries = [
            ('España', 'ES'), ('México', 'MX'), ('Argentina', 'AR'), 
            ('Colombia', 'CO'), ('Chile', 'CL'), ('Perú', 'PE'),
            ('Estados Unidos', 'US'), ('Brasil', 'BR')
        ]
        devices = ['mobile', 'desktop', 'tablet']
        device_weights = [0.65, 0.30, 0.05]  # 65% mobile, 30% desktop, 5% tablet
        
        views_created = 0
        for days_back in range(30):
            # Más vistas en días recientes
            base_views = max(1, 50 - days_back)
            daily_views = random.randint(int(base_views * 0.8), int(base_views * 1.2))
            
            for _ in range(daily_views):
                country, country_code = random.choice(countries)
                device = random.choices(devices, weights=device_weights)[0]
                
                # Timestamp aleatorio dentro del día
                base_time = timezone.now() - timedelta(days=days_back)
                random_time = base_time + timedelta(
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                ProfileView.objects.create(
                    profile=profile,
                    timestamp=random_time,
                    ip_address=f"192.168.1.{random.randint(1, 254)}",
                    user_agent=f"Mozilla/5.0 ({device})",
                    device_type=device,
                    country=country,
                    country_code=country_code
                )
                views_created += 1
        
        print(f"✅ Creadas {views_created} vistas de perfil")
        
        # Crear clicks en enlaces
        print("🔗 Creando clicks en enlaces...")
        clicks_created = 0
        
        for days_back in range(30):
            # Más clicks en días recientes
            base_clicks = max(1, 30 - days_back)
            daily_clicks = random.randint(int(base_clicks * 0.7), int(base_clicks * 1.3))
            
            for _ in range(daily_clicks):
                # Seleccionar enlace aleatorio (con pesos)
                link_weights = [3, 2, 2, 1, 1]  # Instagram y YouTube más populares
                if len(links) >= len(link_weights):
                    link = random.choices(links[:len(link_weights)], weights=link_weights)[0]
                else:
                    link = random.choice(links)
                
                country, country_code = random.choice(countries)
                device = random.choices(devices, weights=device_weights)[0]
                
                # Timestamp aleatorio dentro del día
                base_time = timezone.now() - timedelta(days=days_back)
                random_time = base_time + timedelta(
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                LinkClick.objects.create(
                    link=link,
                    profile=profile,
                    timestamp=random_time,
                    ip_address=f"10.0.0.{random.randint(1, 254)}",
                    user_agent=f"Mozilla/5.0 ({device})",
                    device_type=device,
                    country=country,
                    country_code=country_code
                )
                clicks_created += 1
        
        print(f"✅ Creados {clicks_created} clicks en enlaces")
        
        # Actualizar contadores legacy
        print("🔄 Actualizando contadores legacy...")
        
        # Actualizar views del perfil
        total_views = ProfileView.objects.filter(profile=profile).count()
        profile.views = total_views
        profile.save()
        
        # Actualizar clicks de enlaces
        for link in links:
            total_clicks = LinkClick.objects.filter(link=link).count()
            link.clicks = total_clicks
            link.save()
        
        print(f"✅ Perfil actualizado: {total_views} vistas")
        
        # Resumen final
        print("\n📈 RESUMEN DE DATOS CREADOS:")
        print(f"   👤 Perfil: {profile.name}")
        print(f"   👁️ Vistas: {total_views}")
        print(f"   🔗 Enlaces: {len(links)}")
        
        total_link_clicks = sum(link.clicks for link in links)
        print(f"   📊 Total clicks: {total_link_clicks}")
        
        for link in links:
            print(f"      • {link.title}: {link.clicks} clicks")
        
        print("\n🎉 ¡Datos de prueba creados exitosamente!")
        print("\nPuedes probar los endpoints:")
        print("   • GET /api/linkinbio/profiles/me/analytics/")
        print("   • GET /api/linkinbio/analytics/detailed/?time_range=7d")
        print("   • GET /api/linkinbio/analytics/devices/?time_range=30d")
        print("   • GET /api/linkinbio/analytics/geography/?time_range=30d")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_test_data()