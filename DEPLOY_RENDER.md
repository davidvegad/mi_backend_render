# 🚀 Despliegue en Render - Sistema Pacifik

## 📋 **Opciones para Auto-Completar Reservas**

### 🎯 **Opción 1: Render Cron Jobs (Recomendada)**

Render tiene un servicio específico para cron jobs:

1. **En tu dashboard de Render**:
   - Crea un nuevo servicio
   - Tipo: **Cron Job**
   - Conecta tu repositorio

2. **Configuración**:
   - **Schedule**: `0 0 * * *` (diariamente a las 00:00 UTC)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python manage.py complete_past_reservations`

3. **Variables de Entorno** (usar las mismas del web service):
   - `DATABASE_URL` - Link a tu base de datos PostgreSQL
   - `SECRET_KEY` - Tu clave secreta de Django
   - `DEBUG=False`

### 🎯 **Opción 2: Webhook + Servicio Externo**

Si prefieres usar un servicio externo como cron-job.org:

1. **Configurar API Key** en variables de entorno:
   ```
   CRON_API_KEY=tu-clave-secreta-aqui
   ```

2. **URL del webhook**:
   ```
   https://tu-app.onrender.com/api/pacifik/cron/complete-reservations/
   ```

3. **Servicios recomendados**:
   - [cron-job.org](https://cron-job.org) - Gratis
   - [EasyCron](https://www.easycron.com) - Gratis/Pago
   - [Zapier](https://zapier.com) - Automatización

4. **Configuración del cron externo**:
   - **Método**: POST
   - **URL**: `https://tu-app.onrender.com/api/pacifik/cron/complete-reservations/`
   - **Headers**: `X-API-Key: tu-clave-secreta-aqui`
   - **Frecuencia**: Diariamente a las 00:00

### 🎯 **Opción 3: GitHub Actions (Gratis)**

Crear workflow en `.github/workflows/daily-cron.yml`:

```yaml
name: Daily Auto-Complete Reservations

on:
  schedule:
    - cron: '0 0 * * *'  # Diariamente a las 00:00 UTC

jobs:
  complete-reservations:
    runs-on: ubuntu-latest
    steps:
      - name: Call Webhook
        run: |
          curl -X POST \
            -H "X-API-Key: ${{ secrets.CRON_API_KEY }}" \
            https://tu-app.onrender.com/api/pacifik/cron/complete-reservations/
```

## 🔧 **Configuración de Producción**

### Variables de Entorno Necesarias:

```bash
# Base de datos
DATABASE_URL=postgresql://...

# Django
SECRET_KEY=tu-clave-secreta
DEBUG=False
ALLOWED_HOSTS=tu-app.onrender.com

# Para cron webhook (Opción 2)
CRON_API_KEY=una-clave-secreta-fuerte

# Email (si usas)
SENDGRID_API_KEY=tu-api-key
DEFAULT_FROM_EMAIL=noreply@tudominio.com
```

### Build Command:
```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
```

### Start Command:
```bash
gunicorn core.wsgi:application
```

## 📊 **Monitoreo**

### Logs del Cron Job:

**Opción 1 (Render Cron)**: Ver logs en dashboard de Render

**Opción 2 (Webhook)**: Los logs aparecen en:
```
GET https://tu-app.onrender.com/api/pacifik/cron/complete-reservations/
```

### Verificar Ejecución:

Endpoint de prueba manual:
```bash
curl -X POST \
  -H "X-API-Key: tu-clave-secreta" \
  https://tu-app.onrender.com/api/pacifik/cron/complete-reservations/
```

## ⚠️ **Consideraciones Importantes**

1. **Zona Horaria**: Render usa UTC. Ajusta horarios según tu zona.

2. **Base de Datos**: Asegúrate que el cron job use la misma DB que tu app principal.

3. **Costos**: 
   - Render Cron Jobs: Pueden tener costo según el plan
   - Servicios externos: Muchos ofrecen planes gratuitos
   - GitHub Actions: 2000 minutos gratis/mes

4. **Backup**: El comando es seguro pero considera hacer backups de DB.

## 🧪 **Testing**

1. **Desarrollo**: `python manage.py complete_past_reservations`

2. **Producción**: Llamar el webhook manualmente primero

3. **Verificar**: Revisar logs y base de datos

## 📝 **Recomendación Final**

**Para proyectos pequeños/medianos**: Usar **GitHub Actions** (gratis y confiable)

**Para proyectos empresariales**: Usar **Render Cron Jobs** (integrado y profesional)