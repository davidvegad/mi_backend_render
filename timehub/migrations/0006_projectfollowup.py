# Generated manually for ProjectFollowUp model

import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timehub', '0005_alter_leaverequest_attachment'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Solo crear modelo ProjectFollowUp
        migrations.CreateModel(
            name='ProjectFollowUp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('follow_up_date', models.DateField(help_text='Fecha de la reunión de seguimiento')),
                ('status', models.CharField(
                    choices=[
                        ('ON_TRACK', 'En Curso'), 
                        ('AT_RISK', 'En Riesgo'), 
                        ('DELAYED', 'Retrasado'), 
                        ('BLOCKED', 'Bloqueado'), 
                        ('COMPLETED', 'Completado'), 
                        ('CANCELLED', 'Cancelado')
                    ], 
                    default='ON_TRACK', 
                    max_length=15
                )),
                ('progress_percentage', models.DecimalField(
                    decimal_places=2, 
                    help_text='% de avance del proyecto', 
                    max_digits=5, 
                    validators=[
                        django.core.validators.MinValueValidator(Decimal('0.00')), 
                        django.core.validators.MaxValueValidator(Decimal('100.00'))
                    ]
                )),
                ('observations', models.TextField(help_text='Observaciones de la reunión')),
                ('logged_hours', models.DecimalField(
                    decimal_places=2, 
                    help_text='Horas imputadas hasta la fecha', 
                    max_digits=8, 
                    validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]
                )),
                ('hours_percentage', models.DecimalField(
                    decimal_places=2, 
                    help_text='% de horas utilizadas', 
                    max_digits=5, 
                    validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]
                )),
                ('estimated_completion_date', models.DateField(
                    blank=True, 
                    help_text='Fecha estimada de finalización', 
                    null=True
                )),
                ('next_milestones', models.TextField(blank=True, help_text='Próximos hitos')),
                ('risks', models.TextField(blank=True, help_text='Riesgos identificados')),
                ('actions_required', models.TextField(blank=True, help_text='Acciones requeridas')),
                ('attendees', models.TextField(blank=True, help_text='Asistentes a la reunión')),
                ('meeting_notes', models.TextField(blank=True, help_text='Notas adicionales de la reunión')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, 
                    related_name='created_follow_ups', 
                    to=settings.AUTH_USER_MODEL
                )),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, 
                    related_name='follow_ups', 
                    to='timehub.project'
                )),
            ],
            options={
                'ordering': ['-follow_up_date'],
            },
        ),
        
        # Agregar constraint de unique together
        migrations.AlterUniqueTogether(
            name='projectfollowup',
            unique_together={('project', 'follow_up_date')},
        ),
    ]