# 🧪 Guía de Testing - Sistema de Analytics Completo

## 📋 Pasos para Testear la Integración Frontend-Backend

### **1. Preparar Backend** 🔧

```bash
cd mi_api_backend

# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
# O en Windows: venv\Scripts\activate

# Instalar dependencias nuevas
pip install user-agents==2.2.0

# Verificar migraciones
python manage.py makemigrations links
python manage.py migrate

# Crear datos de prueba
python manage.py shell < create_test_data.py

# Ejecutar servidor
python manage.py runserver
```

### **2. Verificar Backend Endpoints** ✅

Testear endpoints directamente (reemplaza `{token}` con tu Bearer token):

```bash
# 1. Analytics básicos
curl -H "Authorization: Bearer {token}" \
     http://localhost:8000/api/linkinbio/profiles/me/analytics/

# 2. Analytics detallados
curl -H "Authorization: Bearer {token}" \
     "http://localhost:8000/api/linkinbio/analytics/detailed/?time_range=7d"

# 3. Estadísticas de dispositivos
curl -H "Authorization: Bearer {token}" \
     "http://localhost:8000/api/linkinbio/analytics/devices/?time_range=7d"

# 4. Estadísticas geográficas
curl -H "Authorization: Bearer {token}" \
     "http://localhost:8000/api/linkinbio/analytics/geography/?time_range=7d"
```

### **3. Preparar Frontend** ⚛️

```bash
cd frontend-link-in-bio

# Instalar dependencias (si es necesario)
npm install

# Configurar variable de entorno
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Ejecutar frontend
npm run dev
```

### **4. Testing Manual del Sistema** 🎯

#### **A. Testear Analytics Básico (`Analytics.tsx`)**

1. **Ir al dashboard:** `http://localhost:3000/dashboard`
2. **Buscar sección de Analytics** (componente básico)
3. **Verificar que muestra:**
   - Total de vistas del perfil
   - Total de clicks
   - CTR (Click-Through Rate)
   - Lista de enlaces con clicks

#### **B. Testear Analytics Detallado (`LinkAnalytics.tsx`)**

1. **Encontrar el componente avanzado** en el dashboard
2. **Verificar que muestra:**
   - ✅ **Métricas generales:** Total clicks, views, CTR
   - ✅ **Gráfico de barras:** Clicks por día (últimos 7 días)
   - ✅ **Dispositivos:** Porcentajes Mobile/Desktop/Tablet
   - ✅ **Países:** Top países con banderas
   - ✅ **Categorías:** Clicks por tipo de enlace
   - ✅ **Actividad reciente:** Lista de clicks recientes

3. **Probar filtros de tiempo:**
   - Cambiar entre "Últimos 7 días", "30 días", "90 días"
   - Verificar que los datos se actualizan

4. **Probar botón "Actualizar":**
   - Click en "Actualizar" debería recargar datos

#### **C. Testear Tracking en Tiempo Real**

1. **Abrir perfil público:** `http://localhost:3000/{tu-slug}`
2. **Hacer clicks en enlaces** del perfil
3. **Volver al dashboard** y refrescar analytics
4. **Verificar que los clicks se registraron**

### **5. Debugging y Logs** 🔍

#### **Frontend (Consola del navegador):**
```javascript
// Verificar token
console.log(localStorage.getItem('accessToken'));

// Logs automáticos del sistema
// - [LinkAnalytics] Intentando cargar datos
// - [LinkAnalytics] Datos cargados exitosamente
// - [LinkAnalytics] Error: Failed to fetch analytics
```

#### **Backend (Terminal del servidor):**
```bash
# Ver requests en tiempo real
python manage.py runserver --verbosity=2

# Verificar datos en BD
python manage.py shell
>>> from links.models import ProfileView, LinkClick
>>> ProfileView.objects.count()
>>> LinkClick.objects.count()
```

### **6. Casos de Prueba Específicos** 🧪

#### **Caso 1: Sin datos**
- **Perfil nuevo sin clicks/views**
- **Esperado:** Analytics muestran zeros, gráficos vacíos
- **No debe:** Fallar o mostrar errores

#### **Caso 2: Token expirado**
- **Simular:** Logout y login
- **Esperado:** Recargar analytics después de login
- **Fallback:** Mostrar datos básicos si falla API

#### **Caso 3: API offline**
- **Simular:** Apagar backend
- **Esperado:** Frontend usa fallback analytics
- **No debe:** Mostrar página en blanco

#### **Caso 4: Diferentes rangos de tiempo**
- **7d:** Datos últimos 7 días
- **30d:** Datos últimos 30 días  
- **90d:** Datos últimos 90 días
- **Verificar:** Diferencias en conteos

### **7. Indicadores de Éxito** ✅

#### **✅ Backend Funcionando:**
- [ ] Migraciones aplicadas sin errores
- [ ] Datos de prueba creados (>100 views, >50 clicks)
- [ ] Endpoints responden con JSON válido
- [ ] Tracking registra nuevos clicks/views

#### **✅ Frontend Funcionando:**
- [ ] Analytics básico carga datos reales
- [ ] Analytics detallado muestra gráficos poblados
- [ ] Filtros de tiempo funcionan
- [ ] Botón refresh actualiza datos
- [ ] No hay errores en consola

#### **✅ Integración Completa:**
- [ ] Clicks en perfil público se reflejan en dashboard
- [ ] Datos son consistentes entre componentes
- [ ] Cache funciona (cambio rápido entre rangos)
- [ ] Fallbacks funcionan si API falla

### **8. Solución de Problemas Comunes** 🛠️

#### **❌ "No authentication token found"**
```bash
# Solución: Hacer login en frontend
# Verificar: localStorage.getItem('accessToken')
```

#### **❌ "Failed to fetch analytics"**
```bash
# Verificar backend esté corriendo
curl http://localhost:8000/api/linkinbio/test/

# Verificar CORS configurado
# Verificar URL en .env.local
```

#### **❌ "Analytics vacíos"**
```bash
# Ejecutar script de datos de prueba otra vez
python manage.py shell < create_test_data.py
```

#### **❌ "Gráficos no se muestran"**
```bash
# Verificar datos en backend
python manage.py shell
>>> from links.analytics_service import AnalyticsService
>>> from links.models import Profile
>>> profile = Profile.objects.first()
>>> service = AnalyticsService(profile)
>>> print(service.get_detailed_analytics('7d'))
```

### **9. Próximos Pasos** 🚀

Una vez que el testing esté completo:

1. **✅ Sistema básico funcionando**
2. **🔄 Optimizaciones:** Cache más inteligente
3. **📊 Más métricas:** Tiempo en página, bounce rate
4. **🎨 UI/UX:** Mejores visualizaciones
5. **📱 Responsive:** Optimizar para móvil
6. **🔐 Seguridad:** Rate limiting, validaciones

---

## 🎯 Resultado Esperado

Al completar este testing, deberías tener:

- **✅ Sistema de analytics completamente funcional**
- **📊 Datos reales en lugar de mocks**
- **🔄 Tracking automático de clicks y vistas**
- **📈 Dashboard con métricas detalladas**
- **🌍 Geolocalización y análisis de dispositivos**
- **⚡ Cache y optimizaciones de rendimiento**

**¡El sistema de analytics está listo para producción!** 🎉