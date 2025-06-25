#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Correr las migraciones para crear las tablas de la BD
python manage.py migrate

# 3. Recolectar los archivos estáticos
python manage.py collectstatic --no-input

# 4. Crear el superusuario de forma no interactiva
#    (leerá las variables de entorno DJANGO_SUPERUSER...)
python manage.py create_admin_user