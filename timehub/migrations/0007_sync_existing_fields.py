# Migración para sincronizar campos que ya existen en la base de datos

import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timehub', '0006_projectfollowup'),
    ]

    operations = [
        # Esta migración está vacía porque los campos ya existen en la base de datos
        # Solo servimos para sincronizar el estado de las migraciones con la BD real
    ]