from django.core.management import call_command
from django.test import TestCase

from accounts.models import User
from hospital.models import Appointment, Department, Doctor, Nurse, Patient


class SeedDemoDataCommandTests(TestCase):
    def test_seed_demo_data_creates_seed_records(self):
        call_command("seed_demo_data")

        self.assertGreater(Department.objects.count(), 0)
        self.assertGreater(Patient.objects.count(), 0)
        self.assertGreater(Doctor.objects.count(), 0)
        self.assertGreater(Nurse.objects.count(), 0)
        self.assertGreater(Appointment.objects.count(), 0)
        self.assertTrue(User.objects.filter(username="doctor.smith").exists())
