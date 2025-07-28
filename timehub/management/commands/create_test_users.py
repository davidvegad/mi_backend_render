from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from timehub.models import UserProfile, Client, Project, Assignment
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Create test users for TimeHub'

    def handle(self, *args, **options):
        self.stdout.write('Creating test users...')

        # Crear usuarios de prueba
        users_data = [
            {
                'username': 'juan.perez@empresa.com',
                'email': 'juan.perez@empresa.com',
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'password': 'password123'
            },
            {
                'username': 'maria.garcia@empresa.com',
                'email': 'maria.garcia@empresa.com',
                'first_name': 'María',
                'last_name': 'García',
                'password': 'password123'
            },
            {
                'username': 'carlos.rodriguez@empresa.com', 
                'email': 'carlos.rodriguez@empresa.com',
                'first_name': 'Carlos',
                'last_name': 'Rodríguez',
                'password': 'password123'
            }
        ]

        created_users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                email=user_data['email'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name']
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(f'Created user: {user.username}')
                created_users.append(user)
            else:
                self.stdout.write(f'User already exists: {user.username}')
                created_users.append(user)

        # Crear perfiles de usuario
        for user in created_users:
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': f'EMP{user.id:03d}',
                    'department': 'Desarrollo',
                    'position': 'Desarrollador',
                    'weekly_hours': 40.00,
                    'leave_balance_days': 15.00,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created profile for: {user.username}')

        # Asignar usuarios a proyectos específicos para que tengan diferentes proyectos
        projects = list(Project.objects.filter(is_active=True))
        if projects:
            # Juan: Proyectos 1 y 2
            if len(created_users) > 0:
                juan = created_users[0]
                juan_projects = projects[:2] if len(projects) >= 2 else projects
                for project in juan_projects:
                    assignment, created = Assignment.objects.get_or_create(
                        user=juan,
                        project=project,
                        start_date=date.today() - timedelta(days=30),
                        defaults={
                            'role': 'DEVELOPER',
                            'weekly_hours_limit': 20.00,
                            'is_active': True
                        }
                    )
                    if created:
                        self.stdout.write(f'Created assignment: {juan.username} -> {project.code}')

            # María: Proyectos 2 y 3
            if len(created_users) > 1 and len(projects) >= 3:
                maria = created_users[1]
                maria_projects = projects[1:3]
                for project in maria_projects:
                    assignment, created = Assignment.objects.get_or_create(
                        user=maria,
                        project=project,
                        start_date=date.today() - timedelta(days=30),
                        defaults={
                            'role': 'DEVELOPER',
                            'weekly_hours_limit': 25.00,
                            'is_active': True
                        }
                    )
                    if created:
                        self.stdout.write(f'Created assignment: {maria.username} -> {project.code}')

            # Carlos: Solo proyecto 3 y 1 (diferentes combinaciones)
            if len(created_users) > 2 and len(projects) >= 3:
                carlos = created_users[2]
                carlos_projects = [projects[2], projects[0]] if len(projects) > 2 else [projects[0]]
                for project in carlos_projects:
                    assignment, created = Assignment.objects.get_or_create(
                        user=carlos,
                        project=project,
                        start_date=date.today() - timedelta(days=30),
                        defaults={
                            'role': 'TECH_LEAD',
                            'weekly_hours_limit': 30.00,
                            'is_active': True
                        }
                    )
                    if created:
                        self.stdout.write(f'Created assignment: {carlos.username} -> {project.code}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\nTest users created successfully!\n'
                f'You can now log in with:\n'
                f'- juan.perez@empresa.com / password123\n'
                f'- maria.garcia@empresa.com / password123\n'  
                f'- carlos.rodriguez@empresa.com / password123\n'
                f'\nEach user has their own timesheet data.'
            )
        )