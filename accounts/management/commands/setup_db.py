"""
Management command: setup_db
============================
Runs database migrations and ensures a superuser account exists.
Designed to be called once during deployment (e.g. from the Procfile).

Usage:
    python manage.py setup_db

Superuser credentials (override via environment variables):
    DJANGO_SUPERUSER_USERNAME  (default: admin)
    DJANGO_SUPERUSER_EMAIL     (default: admin@grocerytracker.com)
    DJANGO_SUPERUSER_PASSWORD  (default: Admin@123456)
"""

import os

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = "Run migrations and create the superuser if it does not exist."

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _run_migrations(self):
        self.stdout.write(self.style.MIGRATE_HEADING("Applying migrations…"))
        call_command("migrate", "--noinput", verbosity=1)
        self.stdout.write(self.style.SUCCESS("✔  Migrations complete."))

    def _create_superuser(self, username, email, password):
        User = get_user_model()

        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            self.stdout.write(
                self.style.WARNING(
                    f"⚠  Superuser '{username}' already exists — skipping creation."
                )
            )
        else:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"✔  Superuser '{username}' created successfully."
                )
            )

        # Ensure an auth token exists for the superuser (used by DRF token auth).
        token, token_created = Token.objects.get_or_create(user=user)
        if token_created:
            self.stdout.write(
                self.style.SUCCESS(f"✔  Auth token created for '{username}'.")
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠  Auth token for '{username}' already exists — skipping."
                )
            )

        return user

    # ------------------------------------------------------------------ #
    # Entry point                                                          #
    # ------------------------------------------------------------------ #

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.environ.get(
            "DJANGO_SUPERUSER_EMAIL", "admin@grocerytracker.com"
        )
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "Admin@123456")

        # Step 1 — migrations
        self._run_migrations()

        # Step 2 — superuser
        self.stdout.write(self.style.MIGRATE_HEADING("Setting up superuser…"))
        self._create_superuser(username, email, password)

        self.stdout.write(
            self.style.SUCCESS(
                "\n✔  Database setup complete.\n"
                f"   Admin login → username: {username}  |  "
                f"email: {email}\n"
                "   (Set DJANGO_SUPERUSER_PASSWORD env var to override the "
                "default password before first deploy.)"
            )
        )
