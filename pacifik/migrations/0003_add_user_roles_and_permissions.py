# Generated manually for user roles and permissions

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pacifik', '0001_initial'),  # Corregido para apuntar a la migración existente
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='role',
            field=models.CharField(
                choices=[('resident', 'Residente'), ('supervisor', 'Supervisor')],
                default='resident',
                help_text='Rol del usuario en el sistema',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='can_make_reservations',
            field=models.BooleanField(
                default=True,
                help_text='Si el usuario puede crear reservas'
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='can_view_all_reservations',
            field=models.BooleanField(
                default=False,
                help_text='Si el usuario puede ver todas las reservas del edificio'
            ),
        ),
    ]