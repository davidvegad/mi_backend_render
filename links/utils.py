import re
import requests
from django.conf import settings
from user_agents import parse


def get_device_type(user_agent_string):
    """
    Determina el tipo de dispositivo basado en el User-Agent
    """
    if not user_agent_string:
        return 'desktop'
    
    user_agent = parse(user_agent_string)
    
    if user_agent.is_mobile:
        return 'mobile'
    elif user_agent.is_tablet:
        return 'tablet'
    else:
        return 'desktop'


def get_client_ip(request):
    """
    Obtiene la IP real del cliente considerando proxies y load balancers
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_country_from_ip(ip_address):
    """
    Obtiene el país basado en la IP usando un servicio de geolocalización
    Manejo graceful de errores para evitar bloqueos
    """
    # En desarrollo local con IPs privadas, obtener IP pública real
    if settings.DEBUG and (not ip_address or ip_address == '127.0.0.1' or ip_address.startswith('192.168.')):
        try:
            # Obtener IP pública real para testing en desarrollo
            public_ip_response = requests.get('https://api.ipify.org?format=json', timeout=3)
            if public_ip_response.status_code == 200:
                public_ip = public_ip_response.json().get('ip')
                if public_ip:
                    print(f"[DEBUG] IP pública detectada: {public_ip}")
                    return get_country_from_ip(public_ip)  # Recursiva con IP pública
        except Exception as e:
            print(f"[DEBUG] No se pudo obtener IP pública: {e}")
            return 'Desarrollo Local', 'XX'  # Fallback para desarrollo
    
    if not ip_address:
        return 'Unknown', 'XX'
    
    try:
        # Usar ipapi.co (gratuito, 1000 requests/día)
        response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=2)
        if response.status_code == 200:
            data = response.json()
            country = data.get('country_name', 'Unknown')
            country_code = data.get('country_code', 'XX')
            
            # Verificar que no sea error del servicio
            if country and country != 'Undefined':
                return country, country_code
    except Exception as e:
        # Log del error en desarrollo para debugging
        if settings.DEBUG:
            print(f"[DEBUG] Error obteniendo geolocalización para {ip_address}: {e}")
    
    # Fallback: intentar con otro servicio si el primero falla
    try:
        response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                country = data.get('country', 'Unknown')
                country_code = data.get('countryCode', 'XX')
                return country, country_code
    except Exception as e:
        # Log del error en desarrollo para debugging
        if settings.DEBUG:
            print(f"[DEBUG] Error con servicio alternativo para {ip_address}: {e}")
    
    return 'Unknown', 'XX'


def extract_request_metadata(request):
    """
    Extrae toda la metadata relevante de un request para analytics
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    ip_address = get_client_ip(request)
    referrer = request.META.get('HTTP_REFERER', '')
    device_type = get_device_type(user_agent)
    
    # Obtener geolocalización (en producción, considera usar un servicio más robusto)
    country, country_code = get_country_from_ip(ip_address)
    
    return {
        'ip_address': ip_address,
        'user_agent': user_agent,
        'referrer': referrer,
        'device_type': device_type,
        'country': country,
        'country_code': country_code,
    }


def is_bot_request(user_agent_string):
    """
    Detecta si el request viene de un bot/crawler
    """
    if not user_agent_string:
        return False
    
    bot_patterns = [
        r'bot', r'crawler', r'spider', r'scraper',
        r'facebook', r'twitter', r'linkedin',
        r'google', r'bing', r'yahoo', r'duckduck',
        r'telegram', r'whatsapp', r'discord'
    ]
    
    user_agent_lower = user_agent_string.lower()
    return any(re.search(pattern, user_agent_lower) for pattern in bot_patterns)


def should_track_request(request):
    """
    Determina si un request debe ser trackeado para analytics
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # No trackear bots
    if is_bot_request(user_agent):
        return False
    
    # No trackear requests sin User-Agent
    if not user_agent:
        return False
    
    # En desarrollo, permitir tracking para testing
    # if settings.DEBUG and get_client_ip(request) in ['127.0.0.1', '::1']:
    #     return False
    
    return True