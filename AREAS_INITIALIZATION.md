# Inicialización de Áreas Comunes - Pacifik Ocean Tower

## 🏢 Áreas Pre-configuradas

Se han configurado 6 áreas comunes para el edificio:

1. **🏊 Piscina**
   - Cupos: 8 personas por horario
   - Horarios: 6:00 AM - 10:00 PM (lun-vie), 8:00 AM - 10:00 PM (sáb-dom)
   - Duraciones: 2, 3, 4 horas

2. **💪 Gimnasio**
   - Cupos: 6 personas por horario
   - Horarios: 5:00 AM - 11:00 PM (lun-vie), 6:00 AM - 10:00 PM (sáb-dom)
   - Duraciones: 1, 2 horas

3. **🎉 Salón de Eventos**
   - Cupos: 1 reserva por horario
   - Horarios: 10:00 AM - 11:00 PM (lun-jue/dom), hasta 12:00 AM (vie-sáb)
   - Duraciones: 4, 6, 8 horas

4. **🔥 Terraza BBQ**
   - Cupos: 1 reserva por horario
   - Horarios: Solo fines de semana (vie-dom)
   - Duraciones: 4, 6 horas

5. **💼 Business Center**
   - Cupos: 8 personas por horario
   - Horarios: 6:00 AM - 10:00 PM
   - Duraciones: 2, 4, 6 horas

6. **🎾 Cancha de Tenis**
   - Cupos: 4 personas por horario
   - Horarios: 6:00 AM - 10:00 PM (lun-vie), 7:00 AM - 9:00 PM (sáb-dom)
   - Duraciones: 1, 2 horas

## 🚀 Métodos de Inicialización

### 1. Automático en Deploy (RECOMENDADO)
```bash
# Se ejecuta automáticamente en build.sh
python manage.py initialize_areas
```

### 2. Manual en Producción
```bash
# SSH a tu servidor Render
python manage.py initialize_areas
```

### 3. Usando Fixtures
```bash
python manage.py loaddata initial_areas
```

### 4. Reset Completo (CUIDADO)
```bash
# Elimina todas las áreas y reservas
python manage.py reset_areas --confirm
```

## 🔧 Comandos Disponibles

### `initialize_areas`
- ✅ Crea áreas si no existen
- ✅ Actualiza áreas existentes
- ✅ Seguro para re-ejecutar
- ✅ No afecta reservas existentes

### `reset_areas --confirm`
- ⚠️ Elimina TODAS las áreas
- ⚠️ Elimina TODAS las reservas
- ⚠️ Require confirmación explícita
- ✅ Reinicializa áreas después del reset

## 📝 Personalización

Para modificar las áreas, edita:
- `pacifik/management/commands/initialize_areas.py`
- `pacifik/fixtures/initial_areas.json`

Luego ejecuta:
```bash
python manage.py initialize_areas
```

## 🎯 Estrategia de Deployment en Render

1. **Primera vez**: Las áreas se crean automáticamente
2. **Updates**: Las áreas se actualizan sin perder reservas
3. **Rollback**: Usa `reset_areas --confirm` si necesitas empezar de cero

## 🛡️ Seguridad

- ✅ Los comandos son idempotentes
- ✅ No eliminan reservas existentes
- ✅ Actualizan configuraciones sin pérdida de datos
- ✅ Requieren confirmación para operaciones destructivas