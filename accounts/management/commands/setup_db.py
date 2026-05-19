from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Run migrations and create the default admin superuser if not present'

    def handle(self, *args, **options):
        User = get_user_model()

        username = 'admin'
        email = 'admin@grocerytracker.com'
        password = 'Admin@123456'

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(
                f'Superuser "{username}" already exists. Skipping creation.'
            ))
        else:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            self.stdout.write(self.style.SUCCESS(
                f'Superuser "{username}" created successfully.'
            ))
