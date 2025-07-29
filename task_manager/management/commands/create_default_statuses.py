
from django.core.management.base import BaseCommand
from task_manager.models import Status

class Command(BaseCommand):
    help = 'Creates default Kanban board statuses if they do not exist.'

    def handle(self, *args, **options):
        statuses_to_create = [
            {'name': 'Por Hacer', 'order': 1},
            {'name': 'En Progreso', 'order': 2},
            {'name': 'Hecho', 'order': 3},
        ]

        for status_data in statuses_to_create:
            status, created = Status.objects.get_or_create(
                name=status_data['name'],
                defaults={'order': status_data['order']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created status: {status.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Status already exists: {status.name}'))
