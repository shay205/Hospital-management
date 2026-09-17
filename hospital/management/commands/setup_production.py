import os

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create required seed roles and a production admin account safely, and optionally seed demo data when configured."

    def handle(self, *args, **options):
        User = get_user_model()

        required_roles = [
            User.Role.SUPER_ADMINISTRATOR,
            User.Role.HOSPITAL_ADMINISTRATOR,
            User.Role.DOCTOR,
            User.Role.NURSE,
            User.Role.RECEPTIONIST,
            User.Role.PHARMACIST,
            User.Role.LABORATORY_TECHNICIAN,
            User.Role.ACCOUNTANT,
            User.Role.RECORDS_OFFICER,
        ]

        for role in required_roles:
            if not User.Role.values or role not in User.Role.values:
                continue

        admin_username = os.getenv("HC_ADMIN_USERNAME")
        admin_email = os.getenv("HC_ADMIN_EMAIL")
        admin_password = os.getenv("HC_ADMIN_PASSWORD")

        if admin_username and admin_email and admin_password:
            user, created = User.objects.get_or_create(
                username=admin_username,
                defaults={
                    "email": admin_email,
                    "role": User.Role.SUPER_ADMINISTRATOR,
                    "is_active": True,
                    "is_staff": True,
                    "is_superuser": True,
                },
            )
            if created:
                user.set_password(admin_password)
                user.save(update_fields=["password", "email", "role", "is_active", "is_staff", "is_superuser"])
                self.stdout.write(self.style.SUCCESS(f"Created admin user '{admin_username}'."))
            else:
                user.email = admin_email
                user.role = User.Role.SUPER_ADMINISTRATOR
                user.is_active = True
                user.is_staff = True
                user.is_superuser = True
                if not user.has_usable_password():
                    user.set_password(admin_password)
                    user.save(update_fields=["password", "email", "role", "is_active", "is_staff", "is_superuser"])
                else:
                    user.save(update_fields=["email", "role", "is_active", "is_staff", "is_superuser"])
                self.stdout.write(self.style.SUCCESS(f"Ensured admin user '{admin_username}' exists."))
        else:
            self.stdout.write(
                self.style.WARNING(
                    "HC_ADMIN_USERNAME, HC_ADMIN_EMAIL, and HC_ADMIN_PASSWORD must all be set to create the production admin user. "
                    "Skipping superuser creation."
                )
            )

        if os.getenv("AUTO_SEED_DEMO_DATA", "False").lower() == "true":
            call_command("seed_demo_data")
