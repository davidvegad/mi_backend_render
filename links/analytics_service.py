from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Q, Sum, Max
from .models import Profile, ProfileView, LinkClick, Link, SocialIconClick, AnalyticsCache
# Importar cache opcional para evitar errores si no está configurado
try:
    from django.core.cache import cache
    CACHE_AVAILABLE = True
except Exception:
    CACHE_AVAILABLE = False


class AnalyticsService:
    """Servicio para cálculos de analytics complejos"""
    
    def __init__(self, profile):
        self.profile = profile
    
    def get_time_range_filter(self, time_range):
        """Convierte string de time_range a filtro de fecha"""
        now = timezone.now()
        
        if time_range == '7d':
            return now - timedelta(days=7)
        elif time_range == '30d':
            return now - timedelta(days=30)
        elif time_range == '90d':
            return now - timedelta(days=90)
        else:
            return now - timedelta(days=7)  # Default
    
    def get_basic_analytics(self):
        """Analytics básicos para el endpoint existente"""
        total_views = ProfileView.objects.filter(profile=self.profile).count()
        total_clicks = LinkClick.objects.filter(profile=self.profile).count()
        
        # Links data con clicks
        links_data = []
        for link in self.profile.links.all():
            link_clicks = LinkClick.objects.filter(link=link).count()
            links_data.append({
                'id': link.id,
                'title': link.title,
                'url': link.url,
                'clicks': link_clicks
            })
        
        return {
            'total_views': total_views,
            'total_clicks': total_clicks,
            'links_data': links_data
        }
    
    def get_detailed_analytics(self, time_range='7d'):
        """Analytics detallados para LinkAnalytics.tsx"""
        
        # Verificar cache primero (solo si está disponible)
        cached_data = None
        cache_key = f"detailed_analytics_{self.profile.id}_{time_range}"
        if CACHE_AVAILABLE:
            try:
                cached_data = cache.get(cache_key)
                if cached_data:
                    return cached_data
            except Exception:
                pass
        
        start_date = self.get_time_range_filter(time_range)
        
        # Métricas básicas
        total_views = ProfileView.objects.filter(
            profile=self.profile,
            timestamp__gte=start_date
        ).count()
        
        total_clicks = LinkClick.objects.filter(
            profile=self.profile,
            timestamp__gte=start_date
        ).count()
        
        click_through_rate = (total_clicks / total_views * 100) if total_views > 0 else 0
        
        # Top performing link
        top_link_data = LinkClick.objects.filter(
            profile=self.profile,
            timestamp__gte=start_date
        ).values('link__id', 'link__title', 'link__url').annotate(
            click_count=Count('id')
        ).order_by('-click_count').first()
        
        top_performing_link = None
        if top_link_data:
            top_performing_link = {
                'id': top_link_data['link__id'],
                'title': top_link_data['link__title'],
                'url': top_link_data['link__url'],
                'clicks': top_link_data['click_count']
            }
        
        # Recent clicks (últimos 20)
        recent_clicks = LinkClick.objects.filter(
            profile=self.profile,
            timestamp__gte=start_date
        ).select_related('link').order_by('-timestamp')[:20]
        
        # Clicks por día
        clicks_by_day = self._get_clicks_by_day(start_date)
        
        # Clicks por dispositivo
        clicks_by_device = self._get_clicks_by_device(start_date)
        
        # Clicks por país
        clicks_by_country = self._get_clicks_by_country(start_date)
        
        # Clicks por categoría
        clicks_by_category = self._get_clicks_by_category(start_date)
        
        result = {
            'total_clicks': total_clicks,
            'total_views': total_views,
            'click_through_rate': round(click_through_rate, 2),
            'top_performing_link': top_performing_link,
            'recent_clicks': recent_clicks,
            'clicks_by_day': clicks_by_day,
            'clicks_by_device': clicks_by_device,
            'clicks_by_country': clicks_by_country,
            'clicks_by_category': clicks_by_category
        }
        
        # Cachear por 5 minutos (solo si está disponible)
        if CACHE_AVAILABLE:
            try:
                cache.set(cache_key, result, 300)
            except Exception:
                pass
        
        return result
    
    def _get_clicks_by_day(self, start_date):
        """Obtiene clicks agrupados por día"""
        from django.db.models.functions import TruncDate
        from datetime import datetime
        
        # Debug: log para ver qué está pasando
        total_clicks_in_range = LinkClick.objects.filter(
            profile=self.profile,
            timestamp__gte=start_date
        ).count()
        print(f"[DEBUG] Total clicks en rango para perfil {self.profile.id}: {total_clicks_in_range}")
        
        clicks_by_day = LinkClick.objects.filter(
            profile=self.profile,
            timestamp__gte=start_date
        ).extra(
            select={'day': 'DATE(timestamp)'}
        ).values('day').annotate(
            clicks=Count('id')
        ).order_by('day')
        
        # Debug: log de datos raw
        clicks_list = list(clicks_by_day)
        print(f"[DEBUG] Clicks by day raw: {clicks_list}")
        
        # Llenar días faltantes
        result = []
        current_date = start_date.date()
        end_date = timezone.now().date()
        
        # Crear diccionario para búsqueda rápida - FIX: convertir string a date
        clicks_dict = {}
        for item in clicks_list:
            if item['day']:
                # Convertir string YYYY-MM-DD a date object
                day_date = datetime.strptime(str(item['day']), '%Y-%m-%d').date()
                clicks_dict[day_date] = item['clicks']
                print(f"[DEBUG] Agregado al dict: {day_date} -> {item['clicks']}")
        
        while current_date <= end_date:
            clicks_for_day = clicks_dict.get(current_date, 0)
            result.append({
                'date': current_date.strftime('%a %d'),
                'clicks': clicks_for_day
            })
            print(f"[DEBUG] Día {current_date}: {clicks_for_day} clicks")
            current_date += timedelta(days=1)
        
        final_result = result[-7:]  # Solo últimos 7 días
        print(f"[DEBUG] Resultado final: {final_result}")
        return final_result
    
    def _get_clicks_by_device(self, start_date):
        """Obtiene clicks agrupados por dispositivo"""
        device_stats = LinkClick.objects.filter(
            profile=self.profile,
            timestamp__gte=start_date
        ).values('device_type').annotate(
            clicks=Count('id')
        ).order_by('-clicks')
        
        total_clicks = sum(stat['clicks'] for stat in device_stats)
        
        result = []
        device_mapping = {
            'mobile': 'Mobile',
            'desktop': 'Desktop',
            'tablet': 'Tablet'
        }
        
        for stat in device_stats:
            device_name = device_mapping.get(stat['device_type'], 'Unknown')
            percentage = (stat['clicks'] / total_clicks * 100) if total_clicks > 0 else 0
            result.append({
                'device': device_name,
                'clicks': stat['clicks'],
                'percentage': round(percentage, 1)
            })
        
        return result
    
    def _get_clicks_by_country(self, start_date):
        """Obtiene clicks agrupados por país"""
        country_stats = LinkClick.objects.filter(
            profile=self.profile,
            timestamp__gte=start_date
        ).values('country', 'country_code').annotate(
            clicks=Count('id')
        ).order_by('-clicks')[:10]  # Top 10 países
        
        # Mapeo de banderas (emojis de país) - expandido
        flag_mapping = {
            'ES': '🇪🇸', 'MX': '🇲🇽', 'AR': '🇦🇷', 'CO': '🇨🇴',
            'CL': '🇨🇱', 'PE': '🇵🇪', 'US': '🇺🇸', 'CA': '🇨🇦',
            'BR': '🇧🇷', 'VE': '🇻🇪', 'EC': '🇪🇨', 'UY': '🇺🇾',
            'PY': '🇵🇾', 'BO': '🇧🇴', 'CR': '🇨🇷', 'PA': '🇵🇦',
            'GT': '🇬🇹', 'HN': '🇭🇳', 'SV': '🇸🇻', 'NI': '🇳🇮',
            'FR': '🇫🇷', 'IT': '🇮🇹', 'DE': '🇩🇪', 'GB': '🇬🇧',
            # Más países comunes
            'AU': '🇦🇺', 'IN': '🇮🇳', 'JP': '🇯🇵', 'KR': '🇰🇷',
            'CN': '🇨🇳', 'RU': '🇷🇺', 'ZA': '🇿🇦', 'NG': '🇳🇬',
            'EG': '🇪🇬', 'MA': '🇲🇦', 'KE': '🇰🇪', 'GH': '🇬🇭',
            'SG': '🇸🇬', 'TH': '🇹🇭', 'VN': '🇻🇳', 'PH': '🇵🇭',
            'ID': '🇮🇩', 'MY': '🇲🇾', 'BD': '🇧🇩', 'PK': '🇵🇰',
            'TR': '🇹🇷', 'IL': '🇮🇱', 'SA': '🇸🇦', 'AE': '🇦🇪',
            'XX': '🌍'  # Para países desconocidos
        }
        
        result = []
        for stat in country_stats:
            country_code = stat['country_code'] or 'XX'
            result.append({
                'country': stat['country'] or 'Unknown',
                'country_code': country_code,
                'clicks': stat['clicks'],
                'flag': flag_mapping.get(country_code, '🌍')
            })
        
        return result
    
    def _get_clicks_by_category(self, start_date):
        """Obtiene clicks agrupados por categoría de enlace"""
        category_stats = LinkClick.objects.filter(
            profile=self.profile,
            timestamp__gte=start_date
        ).values('link__type').annotate(
            clicks=Count('id')
        ).order_by('-clicks')
        
        # Mapeo de colores y nombres
        category_mapping = {
            'instagram': {'name': 'Instagram', 'color': '#E4405F'},
            'whatsapp': {'name': 'WhatsApp', 'color': '#25D366'},
            'youtube': {'name': 'YouTube', 'color': '#FF0000'},
            'tiktok': {'name': 'TikTok', 'color': '#000000'},
            'x': {'name': 'X (Twitter)', 'color': '#1DA1F2'},
            'facebook': {'name': 'Facebook', 'color': '#1877F2'},
            'generic': {'name': 'Enlaces', 'color': '#6366f1'},
        }
        
        result = []
        for stat in category_stats:
            link_type = stat['link__type']
            category_info = category_mapping.get(link_type, {
                'name': link_type.title(),
                'color': '#6b7280'
            })
            
            result.append({
                'category': category_info['name'],
                'clicks': stat['clicks'],
                'color': category_info['color']
            })
        
        return result
    
    def get_device_stats(self, time_range='7d'):
        """Estadísticas específicas de dispositivos"""
        start_date = self.get_time_range_filter(time_range)
        return self._get_clicks_by_device(start_date)
    
    def get_geography_stats(self, time_range='7d'):
        """Estadísticas específicas geográficas"""
        start_date = self.get_time_range_filter(time_range)
        return self._get_clicks_by_country(start_date)
    
    def get_daily_clicks(self, time_range='7d'):
        """Clicks diarios específicos"""
        start_date = self.get_time_range_filter(time_range)
        return self._get_clicks_by_day(start_date)
    
    def get_recent_activity(self, limit=20):
        """Actividad reciente"""
        return LinkClick.objects.filter(
            profile=self.profile
        ).select_related('link').order_by('-timestamp')[:limit]
    
    def get_realtime_metrics(self):
        """Métricas en tiempo real - últimas 24 horas"""
        from datetime import timedelta
        
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_hour = now - timedelta(hours=1)
        
        # Clicks en la última hora
        clicks_last_hour = LinkClick.objects.filter(
            profile=self.profile,
            timestamp__gte=last_hour
        ).count()
        
        # Clicks en las últimas 24h para comparación
        clicks_last_24h = LinkClick.objects.filter(
            profile=self.profile,
            timestamp__gte=last_24h
        ).count()
        
        # Vistas en la última hora
        views_last_hour = ProfileView.objects.filter(
            profile=self.profile,
            timestamp__gte=last_hour
        ).count()
        
        # Vistas en las últimas 24h
        views_last_24h = ProfileView.objects.filter(
            profile=self.profile,
            timestamp__gte=last_24h
        ).count()
        
        # CTR actual
        ctr_current = (clicks_last_hour / views_last_hour * 100) if views_last_hour > 0 else 0
        
        # Enlaces activos
        active_links = self.profile.links.filter().count()
        
        # Visitantes únicos por IP en la última hora
        unique_visitors = ProfileView.objects.filter(
            profile=self.profile,
            timestamp__gte=last_hour
        ).values('ip_address').distinct().count()
        
        # Calcular tendencias (comparar última hora vs hora anterior)
        hour_before_last = now - timedelta(hours=2)
        clicks_hour_before = LinkClick.objects.filter(
            profile=self.profile,
            timestamp__gte=hour_before_last,
            timestamp__lt=last_hour
        ).count()
        
        views_hour_before = ProfileView.objects.filter(
            profile=self.profile,
            timestamp__gte=hour_before_last,
            timestamp__lt=last_hour
        ).count()
        
        # Calcular cambios porcentuales
        clicks_change = ((clicks_last_hour - clicks_hour_before) / clicks_hour_before * 100) if clicks_hour_before > 0 else 0
        views_change = ((views_last_hour - views_hour_before) / views_hour_before * 100) if views_hour_before > 0 else 0
        
        return {
            'clicks_per_hour': clicks_last_hour,
            'clicks_change': round(clicks_change, 1),
            'clicks_trend': 'up' if clicks_change > 0 else 'down' if clicks_change < 0 else 'stable',
            
            'ctr_current': round(ctr_current, 1),
            'ctr_change': 0,  # Podríamos calcular esto comparando con CTR anterior
            'ctr_trend': 'stable',
            
            'unique_visitors': unique_visitors,
            'visitors_change': round(views_change, 1),
            'visitors_trend': 'up' if views_change > 0 else 'down' if views_change < 0 else 'stable',
            
            'active_links': active_links,
            'links_change': 0,
            'links_trend': 'stable',
            
            'last_updated': now.isoformat()
        }
    
    def get_social_media_stats(self, time_range='7d'):
        """Estadísticas de redes sociales - clicks en iconos sociales"""
        try:
            start_date = self.get_time_range_filter(time_range)
            
            # Clicks por red social
            social_clicks = SocialIconClick.objects.filter(
                profile=self.profile,
                timestamp__gte=start_date
            ).values('social_icon__social_type').annotate(
                clicks=Count('id')
            ).order_by('-clicks')
            
            # Total de clicks en redes sociales
            total_social_clicks = SocialIconClick.objects.filter(
                profile=self.profile,
                timestamp__gte=start_date
            ).count()
            
            # Red social más popular
            most_popular_social = social_clicks.first() if social_clicks else None
            
            # Clicks por día en redes sociales
            social_clicks_by_day = self._get_social_clicks_by_day(start_date)
            
            # Obtener todos los iconos sociales del perfil con sus clicks
            social_icons_with_clicks = []
            for icon in self.profile.social_icons.all():
                click_count = SocialIconClick.objects.filter(
                    social_icon=icon,
                    timestamp__gte=start_date
                ).count()
                
                social_icons_with_clicks.append({
                    'id': icon.id,
                    'social_type': icon.social_type,
                    'social_type_display': icon.get_social_type_display(),
                    'username': icon.username,
                    'url': icon.url,
                    'clicks': click_count
                })
            
            return {
                'total_social_clicks': total_social_clicks,
                'most_popular_social': most_popular_social,
                'social_clicks_by_type': list(social_clicks),
                'social_clicks_by_day': social_clicks_by_day,
                'social_icons_with_clicks': social_icons_with_clicks,
                'time_range': time_range
            }
            
        except Exception as e:
            # Fallback si la tabla SocialIconClick no existe (migraciones pendientes)
            print(f"[SocialMediaStats] Error: {e}")
            print("[SocialMediaStats] Devolviendo datos vacíos - ejecutar migraciones")
            
            # Devolver estructura vacía pero válida
            social_icons_with_clicks = []
            for icon in self.profile.social_icons.all():
                social_icons_with_clicks.append({
                    'id': icon.id,
                    'social_type': icon.social_type,
                    'social_type_display': icon.get_social_type_display(),
                    'username': icon.username,
                    'url': icon.url,
                    'clicks': 0  # Sin datos por falta de migraciones
                })
            
            return {
                'total_social_clicks': 0,
                'most_popular_social': None,
                'social_clicks_by_type': [],
                'social_clicks_by_day': [],
                'social_icons_with_clicks': social_icons_with_clicks,
                'time_range': time_range,
                'needs_migration': True  # Indicador para el frontend
            }
    
    def _get_social_clicks_by_day(self, start_date):
        """Obtiene clicks de redes sociales agrupados por día"""
        try:
            from django.db.models.functions import TruncDate
            
            clicks_by_day = SocialIconClick.objects.filter(
                profile=self.profile,
                timestamp__gte=start_date
            ).extra(
                select={'day': 'DATE(timestamp)'}
            ).values('day').annotate(
                clicks=Count('id')
            ).order_by('day')
            
            # Llenar días faltantes
            result = []
            current_date = start_date.date()
            end_date = timezone.now().date()
            
            # Crear diccionario para búsqueda rápida
            clicks_dict = {}
            for item in clicks_by_day:
                if item['day']:
                    day_date = datetime.strptime(str(item['day']), '%Y-%m-%d').date()
                    clicks_dict[day_date] = item['clicks']
            
            while current_date <= end_date:
                clicks_for_day = clicks_dict.get(current_date, 0)
                result.append({
                    'date': current_date.strftime('%a %d'),
                    'clicks': clicks_for_day
                })
                current_date += timedelta(days=1)
            
            return result[-7:]  # Solo últimos 7 días
            
        except Exception as e:
            print(f"[SocialClicksByDay] Error: {e}")
            # Devolver 7 días con 0 clicks como fallback
            result = []
            current_date = start_date.date()
            for i in range(7):
                date = current_date + timedelta(days=i)
                result.append({
                    'date': date.strftime('%a %d'),
                    'clicks': 0
                })
            return result