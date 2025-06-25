# api/management/commands/create_admin_user.py

import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    """
    Comando para crear un superusuario de forma no interactiva usando
    variables de entorno. Es idempotente, no hará nada si el usuario ya existe.
    """
    help = 'Crea un superusuario si no existe.'

    def handle(self, *args, **options):
        username = os.getenv('DJANGO_SUPERUSER_USERNAME')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

        if not all([username, email, password]):
            self.stdout.write(self.style.ERROR('Faltan las variables de entorno para el superusuario (USERNAME, EMAIL, PASSWORD).'))
            return

        if not User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(f"Creando superusuario '{username}'..."))
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f"Superusuario '{username}' creado exitosamente."))
        else:
            self.stdout.write(self.style.WARNING(f"El superusuario '{username}' ya existe. No se hace nada."))