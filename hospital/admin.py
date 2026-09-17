from django.contrib import admin

from .models import (
    Admission,
    Appointment,
    Bed,
    Department,
    Doctor,
    InsuranceClaim,
    InsuranceProvider,
    InventoryItem,
    InventoryMovement,
    Invoice,
    InvoiceItem,
    LaboratoryTest,
    MedicalRecord,
    Medicine,
    Nurse,
    Patient,
    Payment,
    Prescription,
    Room,
    StockMovement,
    Notification,
    VitalSign,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    search_fields = ("name", "code")


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("patient_id", "first_name", "last_name", "phone", "registration_date", "is_active")
    search_fields = ("patient_id", "first_name", "last_name", "phone", "email")
    list_filter = ("gender", "blood_group", "is_active")


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("doctor_id", "user", "specialization", "department", "status")
    search_fields = ("doctor_id", "user__first_name", "user__last_name", "license_number")
    list_filter = ("department", "status")


@admin.register(Nurse)
class NurseAdmin(admin.ModelAdmin):
    list_display = ("nurse_id", "user", "department", "shift", "status")
    search_fields = ("nurse_id", "user__first_name", "user__last_name", "license_number")
    list_filter = ("department", "shift", "status")


admin.site.register((Room, Bed, Appointment, Admission, MedicalRecord, Prescription, Medicine, StockMovement, LaboratoryTest, Invoice, InvoiceItem, Payment, InsuranceProvider, InsuranceClaim, InventoryItem, InventoryMovement, Notification, VitalSign))
