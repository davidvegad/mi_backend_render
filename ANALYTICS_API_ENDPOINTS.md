# Analytics API Endpoints - Sistema Completo

## 📊 Resumen de Endpoints Implementados

Todos los endpoints requieren autenticación con Bearer Token excepto los de tracking.

### **1. Analytics Básicos** (Compatible con Analytics.tsx existente)
```http
GET /api/linkinbio/profiles/me/analytics/
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "total_views": 1250,
  "total_clicks": 890,
  "links_data": [
    {
      "id": 1,
      "title": "Mi Instagram",
      "url": "https://instagram.com/user",
      "clicks": 456
    }
  ]
}
```

### **2. Analytics Detallados** (Para LinkAnalytics.tsx)
```http
GET /api/linkinbio/analytics/detailed/?time_range=7d
Authorization: Bearer {token}
```

**Parámetros:**
- `time_range`: `7d` | `30d` | `90d` (default: 7d)

**Respuesta:**
```json
{
  "total_clicks": 890,
  "total_views": 1250,
  "click_through_rate": 71.2,
  "top_performing_link": {
    "id": 1,
    "title": "Mi Instagram",
    "url": "https://instagram.com/user",
    "clicks": 456
  },
  "recent_clicks": [
    {
      "id": 123,
      "link": 1,
      "link_title": "Mi Instagram",
      "timestamp": "2025-07-23T10:30:00Z",
      "device_type": "mobile",
      "country": "España",
      "country_code": "ES"
    }
  ],
  "clicks_by_day": [
    {"date": "Lun 22", "clicks": 125},
    {"date": "Mar 23", "clicks": 89}
  ],
  "clicks_by_device": [
    {"device": "Mobile", "clicks": 567, "percentage": 63.7},
    {"device": "Desktop", "clicks": 323, "percentage": 36.3}
  ],
  "clicks_by_country": [
    {"country": "España", "country_code": "ES", "clicks": 245, "flag": "🇪🇸"},
    {"country": "México", "country_code": "MX", "clicks": 123, "flag": "🇲🇽"}
  ],
  "clicks_by_category": [
    {"category": "Instagram", "clicks": 456, "color": "#E4405F"},
    {"category": "Enlaces", "clicks": 234, "color": "#6366f1"}
  ]
}
```

### **3. Estadísticas de Dispositivos**
```http
GET /api/linkinbio/analytics/devices/?time_range=7d
Authorization: Bearer {token}
```

**Respuesta:**
```json
[
  {"device": "Mobile", "clicks": 567, "percentage": 63.7},
  {"device": "Desktop", "clicks": 323, "percentage": 36.3},
  {"device": "Tablet", "clicks": 0, "percentage": 0.0}
]
```

### **4. Estadísticas Geográficas**
```http
GET /api/linkinbio/analytics/geography/?time_range=7d
Authorization: Bearer {token}
```

**Respuesta:**
```json
[
  {"country": "España", "country_code": "ES", "clicks": 245, "flag": "🇪🇸"},
  {"country": "México", "country_code": "MX", "clicks": 123, "flag": "🇲🇽"},
  {"country": "Argentina", "country_code": "AR", "clicks": 89, "flag": "🇦🇷"}
]
```

### **5. Clicks Diarios**
```http
GET /api/linkinbio/analytics/daily/?time_range=7d
Authorization: Bearer {token}
```

**Respuesta:**
```json
[
  {"date": "Lun 17", "clicks": 45},
  {"date": "Mar 18", "clicks": 67},
  {"date": "Mié 19", "clicks": 89},
  {"date": "Jue 20", "clicks": 123},
  {"date": "Vie 21", "clicks": 156},
  {"date": "Sáb 22", "clicks": 134},
  {"date": "Dom 23", "clicks": 89}
]
```

### **6. Actividad Reciente**
```http
GET /api/linkinbio/analytics/recent-activity/?limit=20
Authorization: Bearer {token}
```

**Parámetros:**
- `limit`: número de clicks recientes (default: 20)

**Respuesta:**
```json
[
  {
    "id": 789,
    "link": 1,
    "link_title": "Mi Instagram",
    "timestamp": "2025-07-23T15:45:30Z",
    "device_type": "mobile",
    "country": "España",
    "country_code": "ES"
  }
]
```

---

## 🔄 Endpoints de Tracking (Sin Autenticación)

### **7. Tracking de Vistas de Perfil** (Actualizado)
```http
POST /api/linkinbio/profile-views/{slug}/
```

**Funcionalidad Mejorada:**
- Mantiene contador legacy (`profile.views += 1`)
- **NUEVO:** Crea registro detallado en `ProfileView` con metadata
- Captura: IP, User-Agent, dispositivo, país, referrer

### **8. Tracking de Clicks de Enlaces** (Actualizado)
```http
GET /api/linkinbio/link-clicks/{link_id}/
```

**Funcionalidad Mejorada:**
- Mantiene contador legacy (`link.clicks += 1`)
- **NUEVO:** Crea registro detallado en `LinkClick` con metadata
- Redirige al URL del enlace
- Captura: IP, User-Agent, dispositivo, país, referrer

---

## 🗄️ Modelos de Base de Datos Creados

### **ProfileView**
```python
class ProfileView(models.Model):
    profile = ForeignKey(Profile)
    timestamp = DateTimeField(auto_now_add=True)
    ip_address = GenericIPAddressField()
    user_agent = TextField()
    referrer = URLField()
    device_type = CharField(choices=['mobile', 'desktop', 'tablet'])
    country = CharField()
    country_code = CharField()
```

### **LinkClick**
```python
class LinkClick(models.Model):
    link = ForeignKey(Link)
    profile = ForeignKey(Profile)
    timestamp = DateTimeField(auto_now_add=True)
    ip_address = GenericIPAddressField()
    user_agent = TextField()
    referrer = URLField()
    device_type = CharField(choices=['mobile', 'desktop', 'tablet'])
    country = CharField()
    country_code = CharField()
```

### **AnalyticsCache**
```python
class AnalyticsCache(models.Model):
    profile = ForeignKey(Profile)
    cache_key = CharField()  # "device_stats_7d", "geo_stats_30d"
    time_range = CharField()  # "7d", "30d", "90d"
    data = JSONField()  # Datos calculados
    created_at = DateTimeField()
    expires_at = DateTimeField()
```

---

## 🚀 Implementación Frontend

### **1. Reemplazar generateMockAnalytics() en LinkAnalytics.tsx**

```typescript
// ANTES (línea 66):
const generateMockAnalytics = (links: LinkData[]): Analytics => {
  // ... código mock
};

// DESPUÉS:
const fetchRealAnalytics = async (timeRange: string): Promise<Analytics> => {
  const accessToken = localStorage.getItem('accessToken');
  const response = await fetch(`${API_URL}/api/linkinbio/analytics/detailed/?time_range=${timeRange}`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch analytics');
  }
  
  return await response.json();
};
```

### **2. Actualizar useEffect en LinkAnalytics.tsx**

```typescript
// Reemplazar línea 193:
const newAnalytics = generateMockAnalytics(links);

// Por:
const newAnalytics = await fetchRealAnalytics(timeRange);
```

### **3. Analytics.tsx ya está conectado** ✅
El componente `Analytics.tsx` ya usa el endpoint real `/api/linkinbio/profiles/me/analytics/`.

---

## 📋 Pasos de Instalación

### **1. Instalar Dependencia**
```bash
cd mi_api_backend
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install user-agents==2.2.0
```

### **2. Crear Migraciones**
```bash
python manage.py makemigrations links
python manage.py migrate
```

**O ejecutar SQL manual:**
```bash
python manage.py dbshell < migration_sql.sql
```

### **3. Verificar Endpoints**
```bash
python manage.py runserver
# Testear: http://localhost:8000/api/linkinbio/analytics/detailed/
```

---

## 🎯 Beneficios Implementados

### **Compatibilidad Total**
- ✅ `Analytics.tsx` sigue funcionando (endpoint existente mejorado)
- ✅ Tracking existente mantiene contadores legacy
- ✅ Nuevos datos detallados se capturan automáticamente

### **Funcionalidades Nuevas**
- 📊 **Analytics detallados** para `LinkAnalytics.tsx`
- 🌍 **Geolocalización** automática por IP
- 📱 **Detección de dispositivos** avanzada
- ⚡ **Cache inteligente** (5 minutos)
- 🔄 **Filtros por tiempo** (7d, 30d, 90d)

### **Optimización**
- 📈 **Índices de BD** para queries rápidas
- 🗃️ **Sistema de cache** para métricas pesadas
- 🤖 **Filtrado de bots** automático
- 🔒 **Validación de requests** de tracking

---

## 🧪 Testing

### **Datos de Prueba**
Para generar datos de prueba, puedes crear clicks simulados:

```python
# En Django shell: python manage.py shell
from links.models import *
from links.utils import extract_request_metadata

profile = Profile.objects.first()
link = profile.links.first()

# Crear clicks de prueba
for i in range(50):
    LinkClick.objects.create(
        link=link,
        profile=profile,
        device_type='mobile' if i % 2 else 'desktop',
        country='España' if i % 3 else 'México',
        country_code='ES' if i % 3 else 'MX'
    )
```

El sistema está **listo para uso inmediato** y mantendrá compatibilidad total con el frontend existente mientras añade las nuevas capacidades de analytics detallados.