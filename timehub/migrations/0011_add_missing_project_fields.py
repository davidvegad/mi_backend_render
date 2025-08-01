# Agregar campos faltantes al modelo Project de manera segura
from django.db import migrations, models, connection
from decimal import Decimal
import django.core.validators


def add_fields_conditionally(apps, schema_editor):
    """Add fields only if they don't already exist"""
    db_vendor = connection.vendor
    
    with connection.cursor() as cursor:
        # Define the fields we want to add
        fields_to_check = ['approved_hours', 'budget', 'priority', 'project_type']
        
        # Check which fields already exist
        existing_fields = []
        for field_name in fields_to_check:
            if db_vendor == 'postgresql':
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.columns 
                    WHERE table_name='timehub_project' AND column_name=%s
                """, [field_name])
                if cursor.fetchone()[0] > 0:
                    existing_fields.append(field_name)
            else:  # SQLite
                cursor.execute("PRAGMA table_info(timehub_project)")
                columns = [row[1] for row in cursor.fetchall()]
                if field_name in columns:
                    existing_fields.append(field_name)
        
        # Only proceed with AddField operations for non-existing fields
        Project = apps.get_model('timehub', 'Project')
        
        # Add approved_hours if it doesn't exist
        if 'approved_hours' not in existing_fields:
            schema_editor.add_field(
                Project,
                models.DecimalField(
                    name='approved_hours',
                    blank=True, 
                    decimal_places=2, 
                    help_text='Horas aprobadas para el proyecto', 
                    max_digits=8, 
                    null=True, 
                    validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]
                )
            )
            print("✅ Added approved_hours field")
        else:
            print("⚠️  approved_hours field already exists")
            
        # Add budget if it doesn't exist
        if 'budget' not in existing_fields:
            schema_editor.add_field(
                Project,
                models.DecimalField(
                    name='budget',
                    blank=True, 
                    decimal_places=2, 
                    help_text='Presupuesto del proyecto', 
                    max_digits=12, 
                    null=True, 
                    validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]
                )
            )
            print("✅ Added budget field")
        else:
            print("⚠️  budget field already exists")
            
        # Add priority if it doesn't exist
        if 'priority' not in existing_fields:
            schema_editor.add_field(
                Project,
                models.CharField(
                    name='priority',
                    choices=[
                        ('LOW', 'Low'), 
                        ('MEDIUM', 'Medium'), 
                        ('HIGH', 'High'), 
                        ('CRITICAL', 'Critical')
                    ], 
                    default='MEDIUM', 
                    help_text='Prioridad del proyecto', 
                    max_length=10
                )
            )
            print("✅ Added priority field")
        else:
            print("⚠️  priority field already exists")
            
        # Add project_type if it doesn't exist
        if 'project_type' not in existing_fields:
            schema_editor.add_field(
                Project,
                models.CharField(
                    name='project_type',
                    blank=True, 
                    choices=[
                        ('FIXED_PRICE', 'Fixed Price'), 
                        ('TIME_MATERIAL', 'Time & Material'), 
                        ('RETAINER', 'Retainer')
                    ], 
                    help_text='Tipo de proyecto', 
                    max_length=20, 
                    null=True
                )
            )
            print("✅ Added project_type field")
        else:
            print("⚠️  project_type field already exists")


def reverse_add_fields(apps, schema_editor):
    """Remove the fields (for migration rollback)"""
    Project = apps.get_model('timehub', 'Project')
    
    # This is a simplified reverse - in production you'd want to check existence first
    try:
        schema_editor.remove_field(Project, Project._meta.get_field('approved_hours'))
    except:
        pass
    try:
        schema_editor.remove_field(Project, Project._meta.get_field('budget'))
    except:
        pass
    try:
        schema_editor.remove_field(Project, Project._meta.get_field('priority'))
    except:
        pass
    try:
        schema_editor.remove_field(Project, Project._meta.get_field('project_type'))
    except:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('timehub', '0010_project_requires_follow_up'),
    ]

    operations = [
        migrations.RunPython(
            add_fields_conditionally,
            reverse_add_fields,
        ),
    ]