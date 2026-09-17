from django.conf import settings
from django.test import SimpleTestCase


class DatabaseSettingsTests(SimpleTestCase):
    def test_default_database_defaults_to_sqlite_for_local_development(self):
        self.assertIn("sqlite3", settings.DATABASES["default"]["ENGINE"])
