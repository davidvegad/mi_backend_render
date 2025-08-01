# Generated manually for evaluation system

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('timehub', '0011_add_missing_project_fields'),
    ]

    operations = [
        # Create EvaluationRole
        migrations.CreateModel(
            name='EvaluationRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre del Rol')),
                ('description', models.TextField(blank=True, verbose_name='Descripción')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Rol de Evaluación',
                'verbose_name_plural': 'Roles de Evaluación',
            },
        ),
        
        # Create ObjectiveCategory
        migrations.CreateModel(
            name='ObjectiveCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('TECHNICAL', 'Desempeño Técnico'), ('COLLABORATION', 'Colaboración y Equipo'), ('GROWTH', 'Formación - Crecimiento')], max_length=20, unique=True, verbose_name='Categoría')),
                ('display_name', models.CharField(max_length=100, verbose_name='Nombre para Mostrar')),
                ('description', models.TextField(blank=True, verbose_name='Descripción')),
                ('order', models.IntegerField(default=0, verbose_name='Orden de Visualización')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Categoría de Objetivo',
                'verbose_name_plural': 'Categorías de Objetivos',
                'ordering': ['order'],
            },
        ),
        
        # Create Quarter
        migrations.CreateModel(
            name='Quarter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(verbose_name='Año')),
                ('quarter', models.CharField(choices=[('Q1', 'Primer Trimestre'), ('Q2', 'Segundo Trimestre'), ('Q3', 'Tercer Trimestre'), ('Q4', 'Cuarto Trimestre')], max_length=2, verbose_name='Trimestre')),
                ('start_date', models.DateField(verbose_name='Fecha de Inicio')),
                ('end_date', models.DateField(verbose_name='Fecha de Fin')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Trimestre',
                'verbose_name_plural': 'Trimestres',
                'ordering': ['-year', '-quarter'],
            },
        ),
        
        # Create Objective
        migrations.CreateModel(
            name='Objective',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Título del Objetivo')),
                ('description', models.TextField(verbose_name='Descripción Detallada')),
                ('weight', models.DecimalField(decimal_places=2, default=Decimal('1.00'), max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='Peso del Objetivo', help_text='Importancia relativa del objetivo (usado para cálculos ponderados)')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timehub.objectivecategory', verbose_name='Categoría')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timehub.evaluationrole', verbose_name='Rol')),
            ],
            options={
                'verbose_name': 'Objetivo',
                'verbose_name_plural': 'Objetivos',
                'ordering': ['role', 'category', 'title'],
            },
        ),
        
        # Create EmployeeEvaluation
        migrations.CreateModel(
            name='EmployeeEvaluation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('ASSIGNED', 'Objetivos Asignados'), ('IN_PROGRESS', 'En Progreso'), ('PENDING_REVIEW', 'Pendiente de Revisión'), ('COMPLETED', 'Completada'), ('CANCELLED', 'Cancelada')], default='ASSIGNED', max_length=20, verbose_name='Estado')),
                ('assigned_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Asignación')),
                ('objectives_sent_date', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Envío de Objetivos')),
                ('evaluation_completed_date', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Evaluación Completada')),
                ('assignment_notes', models.TextField(blank=True, verbose_name='Notas de Asignación')),
                ('evaluation_notes', models.TextField(blank=True, verbose_name='Notas de Evaluación')),
                ('overall_score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0')), django.core.validators.MaxValueValidator(Decimal('100'))], verbose_name='Puntuación General (%)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evaluations', to='auth.user', verbose_name='Empleado')),
                ('quarter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timehub.quarter', verbose_name='Trimestre')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timehub.evaluationrole', verbose_name='Rol Asignado')),
                ('supervisor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supervised_evaluations', to='auth.user', verbose_name='Jefe de Proyecto')),
            ],
            options={
                'verbose_name': 'Evaluación de Empleado',
                'verbose_name_plural': 'Evaluaciones de Empleados',
                'ordering': ['-quarter__year', '-quarter__quarter', 'employee__last_name'],
            },
        ),
        
        # Create EvaluationObjective
        migrations.CreateModel(
            name='EvaluationObjective',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('custom_description', models.TextField(blank=True, verbose_name='Descripción Personalizada', help_text='Si se especifica, reemplaza la descripción del objetivo base')),
                ('custom_weight', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='Peso Personalizado')),
                ('score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0')), django.core.validators.MaxValueValidator(Decimal('100'))], verbose_name='Calificación (%)')),
                ('evaluator_comments', models.TextField(blank=True, verbose_name='Comentarios del Evaluador')),
                ('employee_comments', models.TextField(blank=True, verbose_name='Comentarios del Empleado')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('evaluated_at', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Evaluación')),
                ('evaluation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='objectives', to='timehub.employeeevaluation', verbose_name='Evaluación')),
                ('objective', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timehub.objective', verbose_name='Objetivo')),
            ],
            options={
                'verbose_name': 'Objetivo de Evaluación',
                'verbose_name_plural': 'Objetivos de Evaluación',
                'ordering': ['objective__category__order', 'objective__title'],
            },
        ),
        
        # Create EvaluationAttachment
        migrations.CreateModel(
            name='EvaluationAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='evaluation_attachments/', verbose_name='Archivo')),
                ('filename', models.CharField(max_length=255, verbose_name='Nombre del Archivo')),
                ('file_size', models.BigIntegerField(verbose_name='Tamaño del Archivo (bytes)')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Subida')),
                ('evaluation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='timehub.employeeevaluation', verbose_name='Evaluación')),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user', verbose_name='Subido por')),
            ],
            options={
                'verbose_name': 'Adjunto de Evaluación',
                'verbose_name_plural': 'Adjuntos de Evaluación',
                'ordering': ['-uploaded_at'],
            },
        ),
        
        # Add constraints
        migrations.AddConstraint(
            model_name='quarter',
            constraint=models.UniqueConstraint(fields=('year', 'quarter'), name='unique_year_quarter'),
        ),
        migrations.AddConstraint(
            model_name='objective',
            constraint=models.UniqueConstraint(fields=('role', 'category', 'title'), name='unique_role_category_title'),
        ),
        migrations.AddConstraint(
            model_name='employeeevaluation',
            constraint=models.UniqueConstraint(fields=('employee', 'quarter'), name='unique_employee_quarter'),
        ),
        migrations.AddConstraint(
            model_name='evaluationobjective',
            constraint=models.UniqueConstraint(fields=('evaluation', 'objective'), name='unique_evaluation_objective'),
        ),
    ]