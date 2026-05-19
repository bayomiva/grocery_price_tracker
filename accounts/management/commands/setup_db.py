from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@grocerytracker.com"
ADMIN_PASSWORD = "Admin@123456"


class Command(BaseCommand):
    help = "Initialize the database and create the admin user if it does not exist"

    def handle(self, *args, **options):
        self.stdout.write("Running setup_db...")

        if User.objects.filter(username=ADMIN_USERNAME).exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Admin user '{ADMIN_USERNAME}' already exists. Skipping creation."
                )
            )
        else:
            User.objects.create_superuser(
                username=ADMIN_USERNAME,
                email=ADMIN_EMAIL,
                password=ADMIN_PASSWORD,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Admin user '{ADMIN_USERNAME}' created successfully."
                )
            )
