# 🔗 EnlacePro - Contexto del Proyecto

## 📋 Descripción General
EnlacePro es una plataforma tipo "link in bio" desarrollada con **Django REST Framework** (backend) y **Next.js 14** (frontend). Permite a los usuarios crear perfiles personalizados con enlaces, iconos sociales, y analytics avanzados.

## 🏗️ Arquitectura del Sistema

### **Backend (Django REST Framework)**
- **Ubicación**: `/mnt/c/Users/davi_/Documents/Render/mi_api_backend/`
- **Base de datos**: PostgreSQL en producción, SQLite en desarrollo
- **Autenticación**: JWT con tokens de acceso y refresh
- **Almacenamiento**: AWS S3 para archivos multimedia

### **Frontend (Next.js 14)**
- **Ubicación**: `/mnt/c/Users/davi_/Documents/Render/frontend-link-in-bio/`
- **Framework**: Next.js 14 con App Router
- **Styling**: Tailwind CSS
- **Estado**: React hooks (useState, useEffect)

## 🗄️ Modelos de Base de Datos

### **Modelo Principal: Profile**
```python
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    slug = models.SlugField(unique=True)
    
    # Personalización visual
    theme = models.CharField(max_length=50, default='aurora')
    custom_gradient_start = models.CharField(max_length=7, blank=True)
    custom_gradient_end = models.CharField(max_length=7, blank=True)
    background_image = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    background_preference = models.CharField(max_length=10, choices=[('image', 'Image'), ('color', 'Color')], default='color')
    image_overlay = models.CharField(max_length=10, choices=[('none', 'None'), ('dark', 'Dark'), ('light', 'Light')], default='none')
    
    # Estilo de botones
    button_style = models.CharField(max_length=50, default='rounded-lg')
    button_color = models.CharField(max_length=7, default='#000000')
    button_text_color = models.CharField(max_length=7, default='#FFFFFF')
    button_text_opacity = models.FloatField(default=1.0)
    button_background_opacity = models.FloatField(default=1.0)
    button_border_color = models.CharField(max_length=7, default='#000000')
    button_border_opacity = models.FloatField(default=1.0)
    button_shadow_color = models.CharField(max_length=7, default='#000000')
    button_shadow_opacity = models.FloatField(default=1.0)
    
    # Tipografía y CSS personalizado
    font_family = models.CharField(max_length=50, default='font-inter')
    custom_css = models.TextField(blank=True)
    animations = models.JSONField(default=list, blank=True)
```

### **Modelos de Enlaces y Contenido**
```python
class Link(models.Model):
    profile = models.ForeignKey(Profile, related_name='links', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    url = models.URLField()
    type = models.CharField(max_length=50, default='generic')
    order = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)  # Campo legacy

class SocialIcon(models.Model):
    profile = models.ForeignKey(Profile, related_name='social_icons', on_delete=models.CASCADE)
    social_type = models.CharField(max_length=50)
    username = models.CharField(max_length=100)
    url = models.URLField()
    order = models.IntegerField(default=0)
```

### **Modelos de Analytics Avanzados**
```python
class ProfileView(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_type = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    country_code = models.CharField(max_length=2)
    referrer = models.TextField(blank=True)

class LinkClick(models.Model):
    link = models.ForeignKey(Link, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_type = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    country_code = models.CharField(max_length=2)
    referrer = models.TextField(blank=True)

class AnalyticsCache(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    time_range = models.CharField(max_length=10)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```

## 🔌 Endpoints de API

### **Autenticación**
- `POST /api/linkinbio/register/` - Registro de usuario
- `POST /api/linkinbio/token/` - Login (obtener tokens)
- `POST /api/linkinbio/token/refresh/` - Refresh token

### **Perfil y Enlaces**
- `GET/PATCH /api/linkinbio/profiles/me/` - Perfil del usuario autenticado
- `GET /api/linkinbio/profiles/{slug}/` - Perfil público por slug
- `GET /api/linkinbio/profiles/slugs/` - Lista de todos los slugs
- `POST /api/linkinbio/profiles/{slug}/track_view/` - Tracking de vista de perfil
- `GET /api/linkinbio/links/{id}/click/` - Tracking de click en enlace (redirecciona)

### **Analytics**
- `GET /api/linkinbio/analytics/` - Analytics básicos
- `GET /api/linkinbio/analytics/detailed/` - Analytics detallados con filtros de tiempo
- `GET /api/linkinbio/analytics/devices/` - Estadísticas por dispositivo
- `GET /api/linkinbio/analytics/geography/` - Estadísticas geográficas
- `GET /api/linkinbio/analytics/daily/` - Clicks por día
- `GET /api/linkinbio/analytics/recent/` - Actividad reciente

### **Django Admin**
- Interfaces administrativas completas para todos los modelos
- `ProfileAdmin`, `LinkAdmin`, `SocialIconAdmin`
- `ProfileViewAdmin`, `LinkClickAdmin` (solo lectura)
- `AnalyticsCacheAdmin` con filtros avanzados

## 🎨 Características del Frontend

### **Personalización Visual**
- **Temas predefinidos**: 20+ gradientes (Aurora, Sunset, Nebula, etc.)
- **Gradientes personalizados**: Selector de colores para inicio/fin
- **Imágenes de fondo**: Upload con overlays (oscuro/claro/ninguno)
- **Estilos de botones**: 7 estilos (rounded-full, rounded-lg, pill-left, etc.)
- **Colores de botones**: Personalizables con opacidad
- **Tipografías**: Inter, Roboto, Poppins, Montserrat, Open Sans
- **CSS personalizado**: Editor integrado
- **Animaciones**: Fade, Slide, Bounce, Pulse

### **Gestión de Enlaces**
- **Drag & drop**: Reordenamiento visual
- **Tipos de enlaces**: Genérico, Instagram, WhatsApp, YouTube, TikTok, etc.
- **Vista previa en tiempo real**: Mobile y desktop
- **Iconos sociales**: Instagram, Twitter/X, YouTube, TikTok, etc.

### **Analytics Dashboard**
- **Métricas generales**: Total clicks, vistas, CTR
- **Gráficos temporales**: Barras por día
- **Geolocalización**: Países con banderas
- **Dispositivos**: Mobile vs Desktop vs Tablet
- **Actividad reciente**: Últimos 20 clicks
- **Filtros temporales**: 7d, 30d, 90d

## 🔧 Servicios y Utilidades

### **Analytics Service (Backend)**
```python
class AnalyticsService:
    def get_detailed_analytics(self, time_range='7d')
    def _get_clicks_by_day(self, start_date)
    def _get_clicks_by_device(self, start_date)
    def _get_clicks_by_country(self, start_date)
    def _get_clicks_by_category(self, start_date)
```

### **Tracking Utilities**
```python
def get_device_type(user_agent_string)  # Mobile/Desktop/Tablet
def get_client_ip(request)  # IP real considerando proxies
def get_country_from_ip(ip_address)  # Geolocalización via ipapi.co
def should_track_request(request)  # Filtrar bots y requests inválidos
```

### **Style Utilities (Frontend)**
```typescript
getBackgroundAndOverlayStyles(profile: ProfileData)  # Estilos de fondo
getButtonStyles(profile: ProfileData)  # Estilos de botones
getButtonClasses(style?: string)  # Classes CSS de botones
toRgba(hex: string, opacity: number)  # Conversión de colores
```

## 🔄 Estado Actual de Integraciones

### ✅ **Completamente Integrado**
- **Autenticación**: Login, registro, refresh tokens
- **Perfil**: CRUD completo con personalización visual
- **Enlaces**: Gestión, reordenamiento, tracking de clicks
- **Iconos sociales**: CRUD con tipos predefinidos
- **Analytics detallados**: Gráficos, geolocalización, dispositivos
- **Django Admin**: Interfaces completas con permisos
- **Vista pública**: Renderizado de perfiles por slug
- **Tracking**: ProfileView y LinkClick con metadata completa

### ⚠️ **Parcialmente Integrado / Deuda Técnica**
- **Sincronización de clicks**: Analytics avanzados (70 clicks) vs campo legacy (0 clicks)
  - **Problema**: Dos fuentes de datos desconectadas
  - **Impacto**: Botón "Actualizar" no refleja cambios en dashboard principal
  - **Solución temporal**: Implementado `SerializerMethodField` en `LinkSerializer`
  - **Pendiente**: Testing y validación completa

- **Renderizado de banderas emoji**: Solo funciona 🌍, no 🇵🇪 🇪🇸
  - **Problema**: Compatibilidad de navegador/sistema con emojis complejos
  - **Solución implementada**: Códigos de país con colores como fallback
  - **Estado**: Funciona pero podría mejorar experiencia visual

### ❌ **Pendiente de Integración**
- **Métricas en Tiempo Real**: Componente existe pero sin conectar
- **Sistema de notificaciones**: Push notifications configurado pero no usado
- **Export de datos**: Botón existe pero sin funcionalidad
- **Programación de enlaces**: Modal existe pero sin backend
- **Colaboración en equipo**: Componente premium sin implementar
- **Dominio personalizado**: Interfaz sin conectar
- **A/B Testing**: Componente sin backend
- **Integraciones de marketing**: Interfaces sin APIs

## 🏆 Logros Técnicos Recientes

### **Sistema de Analytics Avanzados**
- Implementación completa del tracking de ProfileView y LinkClick
- Geolocalización automática via IP con fallbacks
- Detección de dispositivos mediante User-Agent
- Sistema de cache de analytics con expiración
- Filtros temporales (7d, 30d, 90d) con agregaciones por día
- Interfaces de Django Admin con permisos apropiados

### **Personalización Visual Avanzada**
- Sistema de temas con 20+ gradientes predefinidos
- Editor de gradientes personalizados con color pickers
- Gestión de imágenes de fondo con overlays
- Estilos de botones altamente configurables
- Sistema de animaciones CSS personalizable
- Vista previa en tiempo real para mobile/desktop

### **Optimizaciones de Rendimiento**
- Cache de analytics con invalidación inteligente
- Lazy loading de componentes pesados
- Optimización de queries con select_related/prefetch_related
- Compresión de imágenes y CDN para archivos estáticos
- Paginación en endpoints con gran volumen de datos

## 🔮 Próximos Pasos Sugeridos

### **Prioridad Alta**
1. **Conectar Métricas en Tiempo Real** - Dashboard vacío esperando datos
2. **Implementar Export de Analytics** - Funcionalidad CSV/PDF solicitada
3. **Resolver deuda técnica de clicks** - Unificar completamente los sistemas

### **Prioridad Media**
1. **Sistema de notificaciones push** - Infraestructura lista
2. **Programación de enlaces** - UI completa, falta backend
3. **Mejoras UX en banderas** - Explorar iconos SVG como alternativa

### **Prioridad Baja**
1. **Funciones premium** - A/B testing, colaboración, dominios
2. **Integraciones terceros** - Mailchimp, Google Analytics, etc.
3. **Optimizaciones adicionales** - PWA, offline support

## 📝 Notas de Desarrollo

### **Configuración de Entorno**
- **Backend**: Django 4.2, Python 3.11, PostgreSQL
- **Frontend**: Next.js 14, React 18, Tailwind CSS 3
- **Deploy**: Render.com (backend), Vercel (frontend)
- **Storage**: AWS S3 con CloudFront CDN

### **Patrones de Código**
- **Backend**: ViewSets de DRF con serializers customizados
- **Frontend**: Functional components con hooks customizados  
- **Styling**: Utility-first con Tailwind + componentes reutilizables
- **Estado**: Local state con Context API para datos globales

### **Seguridad**
- JWT con refresh tokens y expiración corta
- CORS configurado para dominios específicos
- Validación de entrada en todos los endpoints
- Rate limiting en endpoints críticos
- Filtrado de bots en sistema de tracking

---

*Última actualización: Enero 2025*
*Versión del proyecto: 2.1.0*