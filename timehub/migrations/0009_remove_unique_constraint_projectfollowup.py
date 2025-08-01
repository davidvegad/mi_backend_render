# Eliminar constraint unique_together para permitir múltiples seguimientos por día

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timehub', '0008_production_sync'),
    ]

    operations = [
        # Eliminar la restricción unique_together
        migrations.AlterUniqueTogether(
            name='projectfollowup',
            unique_together=set(),
        ),
    ]