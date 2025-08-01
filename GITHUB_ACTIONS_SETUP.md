# 🤖 Configuración GitHub Actions - Auto-Completar Reservas

## 📋 **Archivos Creados**

- `.github/workflows/daily-complete-reservations.yml` - Cron job diario
- `.github/workflows/test-cron.yml` - Testing manual

## ⚙️ **Configuración de Secrets en GitHub**

1. **Ve a tu repositorio en GitHub**
2. **Settings** → **Secrets and variables** → **Actions**
3. **Agregar estos Repository Secrets**:

### 🔑 **Secrets Requeridos**:

```bash
# URL de tu backend en Render (sin "/" al final)
BACKEND_URL=https://tu-app-backend.onrender.com

# Clave secreta para el webhook (genera una aleatoria)
CRON_API_KEY=mi-clave-secreta-super-fuerte-123
```

## 🔧 **Pasos de Configuración**

### 1. **Configurar Secrets en GitHub**:

![GitHub Secrets](https://docs.github.com/assets/cb-13947/images/help/repository/secret-new.png)

**BACKEND_URL**:
```
https://tu-app-pacifik-backend.onrender.com
```

**CRON_API_KEY**:
```
pacifik-cron-2024-super-secret-key
```

### 2. **Configurar Variable de Entorno en Render**:

En tu servicio de Render, agregar:
```
CRON_API_KEY=pacifik-cron-2024-super-secret-key
```
(Debe ser exactamente la misma que en GitHub)

### 3. **Verificar la Configuración**:

1. **Push de los archivos** a tu repositorio
2. **Ir a Actions** en GitHub
3. **Ejecutar manualmente** "Test Cron Job (Manual)"
4. **Verificar** que funcione correctamente

## 🕐 **Horarios**

### **Configuración Actual**:
- **Cron**: `0 0 * * *`
- **Significado**: Todos los días a las 00:00 UTC

### **Otras Opciones de Horario**:

```yaml
# A las 06:00 UTC (adjust según tu zona)
- cron: '0 6 * * *'

# A las 23:00 UTC (para completar reservas del día)
- cron: '0 23 * * *'

# Cada 6 horas (para testing)
- cron: '0 */6 * * *'
```

### **Zona Horaria**:
- GitHub Actions usa **UTC**
- Si estás en **Lima (UTC-5)**, las 00:00 UTC = 19:00 Lima (día anterior)
- **Recomendación**: Usar `0 5 * * *` para ejecutar a las 00:00 hora de Lima

## 🧪 **Testing**

### **Test Manual**:
1. **GitHub** → **Actions** → **Test Cron Job (Manual)**
2. **Run workflow** → **Run workflow**
3. **Ver logs** para verificar funcionamiento

### **Test Automático**:
El workflow diario se ejecutará automáticamente. Ver logs en:
**Actions** → **Auto-Complete Daily Reservations**

## 🚨 **Troubleshooting**

### **Error 401 - API Key Inválida**:
- Verificar que `CRON_API_KEY` sea igual en GitHub y Render
- No incluir espacios o caracteres especiales

### **Error 404 - URL No Encontrada**:
- Verificar `BACKEND_URL` sin "/" al final
- Confirmar que el backend esté desplegado

### **Error 500 - Error del Servidor**:
- Revisar logs del backend en Render
- Verificar que la base de datos esté disponible

## 📊 **Monitoreo**

### **Ver Ejecuciones**:
- **GitHub** → **Actions** → Ver historial de ejecuciones
- **Render** → **Logs** → Ver logs del webhook

### **Notificaciones de Fallo**:
GitHub enviará emails automáticamente si el workflow falla.

## ✅ **Ventajas de GitHub Actions**

1. **🆓 Gratis** - 2000 minutos/mes incluidos
2. **🔒 Seguro** - Secrets encriptados
3. **📊 Logs** - Historial completo de ejecuciones
4. **📧 Notificaciones** - Automáticas en caso de fallo
5. **🎯 Control** - Ejecución manual cuando necesites

## 🎯 **Siguiente Paso**

1. **Configurar secrets** en GitHub
2. **Agregar CRON_API_KEY** en Render
3. **Push archivos** al repositorio
4. **Ejecutar test manual**
5. **¡Listo!** 🎉

El sistema auto-completará reservas diariamente sin intervención manual.