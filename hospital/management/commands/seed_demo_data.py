from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from hospital.models import Appointment, Department, Doctor, Nurse, Patient


class Command(BaseCommand):
    help = "Seed the local database with demo hospital records for development and UI testing."

    def handle(self, *args, **options):
        now = timezone.now()

        department_names = [
            ("General Medicine", "MED"),
            ("Emergency", "ER"),
            ("Pediatrics", "PED"),
            ("Orthopedics", "ORT"),
            ("Cardiology", "CARD"),
        ]

        departments = []
        for name, code in department_names:
            dept, _ = Department.objects.get_or_create(
                code=code,
                defaults={"name": name, "description": f"{name} department demo data."},
            )
            if dept.name != name:
                dept.name = name
                dept.save(update_fields=["name"])
            departments.append(dept)

        user_specs = [
            ("doctor.smith", "Doctor", "Smith", User.Role.DOCTOR, departments[0], "MED-1001"),
            ("doctor.ngugi", "Doctor", "Ngugi", User.Role.DOCTOR, departments[4], "CARD-2001"),
            ("nurse.adele", "Nurse", "Adele", User.Role.NURSE, departments[1], "ER-3001"),
            ("nurse.kim", "Nurse", "Kim", User.Role.NURSE, departments[2], "PED-3002"),
        ]

        doctor_users = {}
        nurse_users = {}

        for username, first_name, last_name, role, department, license in user_specs:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": f"{username}@careline.local",
                    "role": role,
                    "phone": "0700000000",
                    "is_active": True,
                },
            )
            if created:
                user.set_password("Password123!")
                user.save(update_fields=["password"])

            if role == User.Role.DOCTOR:
                doctor, _ = Doctor.objects.get_or_create(
                    user=user,
                    defaults={
                        "specialization": "General Practice" if username == "doctor.smith" else "Cardiology",
                        "department": department,
                        "license_number": license,
                        "availability": "Mon-Fri 08:00-17:00",
                    },
                )
                doctor_users[username] = doctor
            else:
                nurse, _ = Nurse.objects.get_or_create(
                    user=user,
                    defaults={
                        "department": department,
                        "license_number": license,
                        "shift": "Day Shift",
                    },
                )
                nurse_users[username] = nurse

        patients = []
        patient_specs = [
            ("Jane", "Doe", "1990-05-12", Patient.Gender.FEMALE, "0701111111", "jane@example.com", "Nairobi"),
            ("John", "Mutua", "1988-02-06", Patient.Gender.MALE, "0702222222", "john@example.com", "Mombasa"),
            ("Amina", "Kiptoo", "2001-11-18", Patient.Gender.FEMALE, "0703333333", "amina@example.com", "Eldoret"),
            ("Peter", "Njeri", "1976-09-08", Patient.Gender.MALE, "0704444444", "peter@example.com", "Nakuru"),
            ("Grace", "Wanjiku", "1995-03-24", Patient.Gender.FEMALE, "0705555555", "grace@example.com", "Kiambu"),
        ]

        for first_name, last_name, dob, gender, phone, email, address in patient_specs:
            patient, _ = Patient.objects.get_or_create(
                first_name=first_name,
                last_name=last_name,
                date_of_birth=dob,
                defaults={
                    "gender": gender,
                    "phone": phone,
                    "email": email,
                    "address": address,
                    "is_active": True,
                },
            )
            patients.append(patient)

        appointment_dates = [
            now + timedelta(days=1, hours=9),
            now + timedelta(days=2, hours=11),
            now + timedelta(days=3, hours=15),
            now + timedelta(days=4, hours=10),
        ]

        for index, start_at in enumerate(appointment_dates):
            doctor = list(doctor_users.values())[index % len(doctor_users)]
            patient = patients[index % len(patients)]
            Appointment.objects.get_or_create(
                doctor=doctor,
                starts_at=start_at,
                defaults={
                    "patient": patient,
                    "department": doctor.department,
                    "reason": "Follow-up consultation",
                    "status": Appointment.Status.SCHEDULED,
                    "notes": "Seeded demo appointment.",
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded demo data: {Department.objects.count()} departments, {Patient.objects.count()} patients, "
                f"{Doctor.objects.count()} doctors, {Nurse.objects.count()} nurses, {Appointment.objects.count()} appointments."
            )
        )
