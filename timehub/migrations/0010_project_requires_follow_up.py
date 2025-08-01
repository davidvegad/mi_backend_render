# Agregar campo requires_follow_up al modelo Project

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timehub', '0009_remove_unique_constraint_projectfollowup'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='requires_follow_up',
            field=models.BooleanField(
                default=True, 
                help_text='Si este proyecto requiere reuniones de seguimiento'
            ),
        ),
    ]