#!/usr/bin/env python
"""
Script to fix migration conflicts in TimeHub project.
The migration 0011 has been updated to check for existing columns before adding them.
This should resolve the "column already exists" error on Render.
"""

import os
import django
from django.core.management import execute_from_command_line
from django.db import connection

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def check_database_connection():
    """Check if we can connect to the database"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def check_migration_status():
    """Check current migration status"""
    try:
        execute_from_command_line(['manage.py', 'showmigrations', 'timehub'])
    except Exception as e:
        print(f"Error checking migrations: {e}")

def check_column_exists():
    """Check if the problematic columns already exist in production"""
    db_vendor = connection.vendor
    
    with connection.cursor() as cursor:
        fields_to_check = ['approved_hours', 'budget', 'priority', 'project_type']
        existing_fields = []
        
        for field_name in fields_to_check:
            try:
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
            except Exception as e:
                print(f"Error checking field {field_name}: {e}")
        
        return existing_fields

def fix_migrations():
    """Fix the migration conflicts"""
    print("=== TimeHub Migration Fix Script ===")
    
    # Check database connection
    if not check_database_connection():
        print("❌ Cannot connect to database. Please check your database settings.")
        return False
    
    print("✅ Database connection successful")
    
    # Check existing columns
    print("\n🔍 Checking existing columns...")
    existing_fields = check_column_exists()
    if existing_fields:
        print(f"⚠️  Found existing fields: {', '.join(existing_fields)}")
        print("✅ The updated migration 0011 will handle these safely")
    else:
        print("ℹ️  No conflicting fields found")
    
    # Show current migration status
    print("\n📋 Current migration status:")
    check_migration_status()
    
    try:
        # Apply migrations normally - the updated 0011 migration handles conflicts
        print("\n🚀 Applying migrations...")
        execute_from_command_line(['manage.py', 'migrate', 'timehub'])
        
        print("\n✅ Migration completed successfully!")
        
        # Show final status
        print("\n📋 Final migration status:")
        check_migration_status()
        
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Check your database connection settings")
        print("2. Ensure you have proper database permissions")
        print("3. Try running migrations manually: python manage.py migrate timehub")
        return False

if __name__ == "__main__":
    success = fix_migrations()
    if success:
        print("\n🎉 All done! Your migrations should now work on Render.")
        print("\n📝 What was fixed:")
        print("   • Updated migration 0011 to check for existing columns")
        print("   • Will skip adding fields that already exist in production")
        print("   • Safe to deploy to Render now")
    else:
        print("\n⚠️  Manual intervention may be required.")