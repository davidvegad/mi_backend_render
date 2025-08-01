# Configuración de Tarea Programada para Auto-Completar Reservas

## Para ejecutar automáticamente a las 00:00 cada día

### En Linux/Mac (Crontab):

1. Abrir crontab:
```bash
crontab -e
```

2. Agregar esta línea:
```bash
0 0 * * * cd /ruta/a/tu/proyecto && ./venv/bin/python manage.py complete_past_reservations
```

### En Windows (Task Scheduler):

1. Abrir "Programador de tareas"
2. Crear tarea básica
3. Nombre: "Auto-completar Reservas Pacifik"
4. Desencadenador: Diariamente a las 00:00
5. Acción: Iniciar programa
6. Programa: `C:\ruta\a\tu\proyecto\venv\Scripts\python.exe`
7. Argumentos: `manage.py complete_past_reservations`
8. Iniciar en: `C:\ruta\a\tu\proyecto\mi_api_backend`

### Ejecución Manual:

Para probar o ejecutar manualmente:
```bash
python manage.py complete_past_reservations
```

### En Producción (Render/Heroku):

Usar servicios de cron jobs como:
- Render Cron Jobs
- Heroku Scheduler
- GitHub Actions (scheduled workflows)

Ejemplo comando:
```bash
python manage.py complete_past_reservations
```