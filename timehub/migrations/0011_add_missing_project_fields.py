# Agregar campos faltantes al modelo Project de manera segura
from django.db import migrations, models
from decimal import Decimal
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('timehub', '0010_project_requires_follow_up'),
    ]

    operations = [
        # Agregar campos usando AddField pero con error handling en caso de que ya existan
        migrations.AddField(
            model_name='project',
            name='approved_hours',
            field=models.DecimalField(
                blank=True, 
                decimal_places=2, 
                help_text='Horas aprobadas para el proyecto', 
                max_digits=8, 
                null=True, 
                validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='budget',
            field=models.DecimalField(
                blank=True, 
                decimal_places=2, 
                help_text='Presupuesto del proyecto', 
                max_digits=12, 
                null=True, 
                validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='priority',
            field=models.CharField(
                choices=[
                    ('LOW', 'Low'), 
                    ('MEDIUM', 'Medium'), 
                    ('HIGH', 'High'), 
                    ('CRITICAL', 'Critical')
                ], 
                default='MEDIUM', 
                help_text='Prioridad del proyecto', 
                max_length=10
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='project_type',
            field=models.CharField(
                blank=True, 
                choices=[
                    ('FIXED_PRICE', 'Fixed Price'), 
                    ('TIME_MATERIAL', 'Time & Material'), 
                    ('RETAINER', 'Retainer')
                ], 
                help_text='Tipo de proyecto', 
                max_length=20, 
                null=True
            ),
            preserve_default=True,
        ),
    ]