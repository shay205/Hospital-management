from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMINISTRATOR = "SUPER_ADMINISTRATOR", "Super Administrator"
        HOSPITAL_ADMINISTRATOR = "HOSPITAL_ADMINISTRATOR", "Hospital Administrator"
        DOCTOR = "DOCTOR", "Doctor"
        NURSE = "NURSE", "Nurse"
        RECEPTIONIST = "RECEPTIONIST", "Receptionist"
        PHARMACIST = "PHARMACIST", "Pharmacist"
        LABORATORY_TECHNICIAN = "LABORATORY_TECHNICIAN", "Laboratory Technician"
        ACCOUNTANT = "ACCOUNTANT", "Accountant"
        RECORDS_OFFICER = "RECORDS_OFFICER", "Records Officer"

    role = models.CharField(max_length=32, choices=Role.choices, default=Role.RECEPTIONIST)
    phone = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_full_name() or self.username
