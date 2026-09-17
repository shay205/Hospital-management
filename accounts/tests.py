import os
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase

from .models import User
from .serializers import LoginSerializer


class DatabaseSettingsTests(SimpleTestCase):
    def test_default_database_defaults_to_sqlite_for_local_development(self):
        self.assertIn("sqlite3", settings.DATABASES["default"]["ENGINE"])


class AuthenticationAndProductionSetupTests(TestCase):
    def test_login_serializer_accepts_email_for_username(self):
        user = User.objects.create_user(username="doctor.admin", email="doctor@example.com", password="StrongPass123!", first_name="Doc")
        data = {"username": "doctor@example.com", "password": "StrongPass123!"}

        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["user"], user)

    @patch.dict(os.environ, {"HC_ADMIN_USERNAME": "admin", "HC_ADMIN_EMAIL": "admin@example.com", "HC_ADMIN_PASSWORD": "StrongPass123!"}, clear=False)
    def test_setup_production_creates_superuser_from_environment(self):
        call_command("setup_production")
        self.assertTrue(User.objects.filter(username="admin", email="admin@example.com").exists())
        self.assertTrue(User.objects.get(username="admin").is_superuser)
