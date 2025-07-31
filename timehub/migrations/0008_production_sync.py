# Migración para sincronizar producción - no hace cambios en la BD

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timehub', '0007_sync_existing_fields'),
    ]

    operations = [
        # Esta migración está vacía porque los campos ya existen en producción
        # Solo marca el estado como sincronizado
    ]