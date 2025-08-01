from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Fix migration conflicts in production'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Check if columns exist
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='timehub_project' 
                AND column_name IN ('approved_hours', 'budget', 'priority', 'project_type')
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]
            
            if len(existing_columns) > 0:
                self.stdout.write(f'Columns already exist: {existing_columns}')
                # Mark migration as fake applied
                call_command('migrate', 'timehub', '0011', fake=True)
                self.stdout.write('Migration marked as applied')
            
            # Apply any remaining migrations
            call_command('migrate')
            self.stdout.write('All migrations applied successfully')