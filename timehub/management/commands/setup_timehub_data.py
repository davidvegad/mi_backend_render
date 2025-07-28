from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import date, timedelta
from timehub.models import Client, Project, Assignment, UserProfile

class Command(BaseCommand):
    help = 'Setup initial TimeHub data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Setting up TimeHub test data...')

        # Obtener el superuser existente
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                self.stdout.write(self.style.ERROR('No superuser found. Please create one first.'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error finding superuser: {e}'))
            return

        # Crear UserProfile para el admin si no existe
        user_profile, created = UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={
                'employee_id': 'EMP001',
                'department': 'Tecnología',
                'position': 'Administrador',
                'weekly_hours': 40.00,
                'leave_balance_days': 15.00,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'Created UserProfile for {admin_user.username}')

        # Crear clientes
        client1, created = Client.objects.get_or_create(
            code='CLI001',
            defaults={
                'name': 'Empresa ABC',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'Created client: {client1.name}')

        client2, created = Client.objects.get_or_create(
            code='CLI002',
            defaults={
                'name': 'Corporación XYZ',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'Created client: {client2.name}')

        # Crear proyectos
        project1, created = Project.objects.get_or_create(
            code='PRJ001',
            defaults={
                'client': client1,
                'name': 'Sistema de Ventas',
                'description': 'Desarrollo de sistema de ventas web',
                'leader': admin_user,
                'start_date': date.today() - timedelta(days=30),
                'is_active': True,
                'progress_percentage': 45.50
            }
        )
        if created:
            self.stdout.write(f'Created project: {project1.name}')

        project2, created = Project.objects.get_or_create(
            code='PRJ002',
            defaults={
                'client': client2,
                'name': 'App Mobile',
                'description': 'Aplicación móvil para clientes',
                'leader': admin_user,
                'start_date': date.today() - timedelta(days=15),
                'is_active': True,
                'progress_percentage': 25.00
            }
        )
        if created:
            self.stdout.write(f'Created project: {project2.name}')

        project3, created = Project.objects.get_or_create(
            code='PRJ003',
            defaults={
                'client': client1,
                'name': 'Dashboard Analytics',
                'description': 'Dashboard de analíticas y reportes',
                'leader': admin_user,
                'start_date': date.today() - timedelta(days=60),
                'is_active': True,
                'progress_percentage': 75.25
            }
        )
        if created:
            self.stdout.write(f'Created project: {project3.name}')

        # Crear asignaciones para el admin
        assignment1, created = Assignment.objects.get_or_create(
            user=admin_user,
            project=project1,
            start_date=date.today() - timedelta(days=30),
            defaults={
                'role': 'PM',
                'weekly_hours_limit': 20.00,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'Created assignment: {admin_user.username} -> {project1.code}')

        assignment2, created = Assignment.objects.get_or_create(
            user=admin_user,
            project=project2,
            start_date=date.today() - timedelta(days=15),
            defaults={
                'role': 'DEVELOPER',
                'weekly_hours_limit': 15.00,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'Created assignment: {admin_user.username} -> {project2.code}')

        assignment3, created = Assignment.objects.get_or_create(
            user=admin_user,
            project=project3,
            start_date=date.today() - timedelta(days=60),
            defaults={
                'role': 'TECH_LEAD',
                'weekly_hours_limit': 10.00,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'Created assignment: {admin_user.username} -> {project3.code}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created TimeHub test data!\n'
                f'User: {admin_user.username}\n'
                f'Clients: {Client.objects.count()}\n'
                f'Projects: {Project.objects.count()}\n'
                f'Assignments: {Assignment.objects.count()}\n'
                f'\nYou can now:\n'
                f'1. Go to http://localhost:3000/timesheet\n'
                f'2. Create time entries for the projects\n'
                f'3. Submit them for approval\n'
            )
        )