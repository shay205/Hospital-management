import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Patient(models.Model):
    class Gender(models.TextChoices):
        FEMALE = "FEMALE", "Female"
        MALE = "MALE", "Male"
        OTHER = "OTHER", "Other"
        UNDISCLOSED = "UNDISCLOSED", "Undisclosed"

    patient_id = models.CharField(max_length=20, unique=True, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=16, choices=Gender.choices)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=200, blank=True)
    insurance_provider = models.CharField(max_length=160, blank=True)
    insurance_number = models.CharField(max_length=80, blank=True)
    blood_group = models.CharField(max_length=8, blank=True)
    allergies = models.TextField(blank=True)
    medical_history = models.TextField(blank=True)
    previous_medications = models.TextField(blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.patient_id:
            self.patient_id = f"PT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient_id} - {self.first_name} {self.last_name}"


class Doctor(models.Model):
    doctor_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="doctor_profile")
    specialization = models.CharField(max_length=120)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="doctors")
    license_number = models.CharField(max_length=80, unique=True)
    availability = models.CharField(max_length=160, blank=True)
    status = models.CharField(max_length=30, default="ACTIVE")

    def save(self, *args, **kwargs):
        if not self.doctor_id:
            self.doctor_id = f"DR-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.doctor_id} - {self.user.get_full_name()}"


class Nurse(models.Model):
    nurse_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="nurse_profile")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="nurses")
    license_number = models.CharField(max_length=80, unique=True)
    shift = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=30, default="ACTIVE")

    def save(self, *args, **kwargs):
        if not self.nurse_id:
            self.nurse_id = f"NR-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nurse_id} - {self.user.get_full_name()}"


class Room(models.Model):
    ward = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="rooms")
    number = models.CharField(max_length=30)
    floor = models.CharField(max_length=30, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("ward", "number"), name="unique_room_per_ward")]

    def __str__(self):
        return f"{self.ward.code} / {self.number}"


class Bed(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        OCCUPIED = "OCCUPIED", "Occupied"
        RESERVED = "RESERVED", "Reserved"
        MAINTENANCE = "MAINTENANCE", "Maintenance"

    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="beds")
    number = models.CharField(max_length=30)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("room", "number"), name="unique_bed_per_room")]

    def __str__(self):
        return f"{self.room} / Bed {self.number}"


class Appointment(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        CONFIRMED = "CONFIRMED", "Confirmed"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        NO_SHOW = "NO_SHOW", "No-show"

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="appointments")
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name="appointments")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="appointments")
    starts_at = models.DateTimeField()
    reason = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("starts_at",)
        constraints = [models.UniqueConstraint(fields=("doctor", "starts_at"), name="unique_doctor_appointment_time")]

    def __str__(self):
        return f"{self.patient} with {self.doctor} at {self.starts_at}"


class Admission(models.Model):
    class Status(models.TextChoices):
        ADMITTED = "ADMITTED", "Admitted"
        DISCHARGED = "DISCHARGED", "Discharged"

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="admissions")
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name="admissions")
    bed = models.ForeignKey(Bed, on_delete=models.PROTECT, related_name="admissions")
    admitted_at = models.DateTimeField()
    diagnosis = models.TextField()
    previous_medical_history = models.TextField(blank=True)
    treatment_notes = models.TextField(blank=True)
    discharged_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ADMITTED)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("patient", "status"), condition=models.Q(status="ADMITTED"), name="one_active_admission_per_patient")]

    def save(self, *args, **kwargs):
        previous_status = None
        if self.pk:
            previous_status = type(self).objects.get(pk=self.pk).status
        super().save(*args, **kwargs)
        if self.status == self.Status.ADMITTED:
            Bed.objects.filter(pk=self.bed_id).update(status=Bed.Status.OCCUPIED)
        elif previous_status == self.Status.ADMITTED or self.status == self.Status.DISCHARGED:
            Bed.objects.filter(pk=self.bed_id).update(status=Bed.Status.AVAILABLE)

    def __str__(self):
        return f"{self.patient} - {self.status}"


class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="medical_records")
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name="medical_records")
    visit_date = models.DateTimeField()
    symptoms = models.TextField(blank=True)
    diagnosis = models.TextField()
    treatment = models.TextField(blank=True)
    medical_history = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    follow_up_instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-visit_date",)


class Prescription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        DISPENSED = "DISPENSED", "Dispensed"
        CANCELLED = "CANCELLED", "Cancelled"

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="prescriptions")
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name="prescriptions")
    medication = models.CharField(max_length=160)
    dosage = models.CharField(max_length=120)
    frequency = models.CharField(max_length=120)
    duration = models.CharField(max_length=120)
    instructions = models.TextField(blank=True)
    prescription_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)


class Medicine(models.Model):
    name = models.CharField(max_length=160)
    stock_quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    expiry_date = models.DateField()
    supplier = models.CharField(max_length=160, blank=True)
    batch_number = models.CharField(max_length=80)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("name", "batch_number"), name="unique_medicine_batch")]

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.reorder_level

    def __str__(self):
        return f"{self.name} ({self.batch_number})"


class StockMovement(models.Model):
    class MovementType(models.TextChoices):
        STOCK_IN = "STOCK_IN", "Stock-in"
        STOCK_OUT = "STOCK_OUT", "Stock-out"

    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT, related_name="stock_movements")
    movement_type = models.CharField(max_length=12, choices=MovementType.choices)
    quantity = models.PositiveIntegerField()
    reference = models.CharField(max_length=120, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="stock_movements")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            delta = self.quantity if self.movement_type == self.MovementType.STOCK_IN else -self.quantity
            Medicine.objects.filter(pk=self.medicine_id).update(stock_quantity=models.F("stock_quantity") + delta)
        super().save(*args, **kwargs)


class LaboratoryTest(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        SAMPLE_COLLECTED = "SAMPLE_COLLECTED", "Sample Collected"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="laboratory_tests")
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name="laboratory_tests")
    test_type = models.CharField(max_length=160)
    sample = models.CharField(max_length=120)
    test_date = models.DateTimeField()
    result = models.TextField(blank=True)
    normal_range = models.CharField(max_length=160, blank=True)
    technician = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="laboratory_tests")
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.REQUESTED)


class Invoice(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        PARTIALLY_PAID = "PARTIALLY_PAID", "Partially paid"
        PAID = "PAID", "Paid"
        VOID = "VOID", "Void"

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="invoices")
    invoice_number = models.CharField(max_length=24, unique=True, editable=False)
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = f"INV-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    @property
    def total(self):
        return sum((item.total for item in self.items.all()), Decimal("0.00"))

    @property
    def paid_amount(self):
        return sum((payment.amount for payment in self.payments.all()), Decimal("0.00"))

    @property
    def outstanding_balance(self):
        return max(self.total - self.paid_amount, Decimal("0.00"))


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    service = models.CharField(max_length=160)
    description = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def total(self):
        return self.quantity * self.unit_price


class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = "CASH", "Cash"
        CARD = "CARD", "Card"
        BANK = "BANK", "Bank"
        MOBILE_MONEY = "MOBILE_MONEY", "Mobile Money"

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="payments")
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=Method.choices)
    reference_number = models.CharField(max_length=120, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="received_payments")


class InsuranceProvider(models.Model):
    name = models.CharField(max_length=160, unique=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    contact_email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class InsuranceClaim(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="insurance_claims")
    provider = models.ForeignKey(InsuranceProvider, on_delete=models.PROTECT, related_name="claims")
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="insurance_claims")
    claim_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    submission_date = models.DateField(null=True, blank=True)
    decision_notes = models.TextField(blank=True)


class InventoryItem(models.Model):
    item = models.CharField(max_length=160, unique=True)
    category = models.CharField(max_length=120)
    quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=40)
    supplier = models.CharField(max_length=160, blank=True)
    reorder_level = models.PositiveIntegerField(default=10)
    expiry_date = models.DateField(null=True, blank=True)


class InventoryMovement(models.Model):
    item = models.ForeignKey(InventoryItem, on_delete=models.PROTECT, related_name="movements")
    movement_type = models.CharField(max_length=12, choices=StockMovement.MovementType.choices)
    quantity = models.PositiveIntegerField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="inventory_movements")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            delta = self.quantity if self.movement_type == StockMovement.MovementType.STOCK_IN else -self.quantity
            InventoryItem.objects.filter(pk=self.item_id).update(quantity=models.F("quantity") + delta)
        super().save(*args, **kwargs)


class VitalSign(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="vital_signs")
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    blood_pressure = models.CharField(max_length=20, blank=True)
    pulse = models.PositiveIntegerField(null=True, blank=True)
    respiratory_rate = models.PositiveIntegerField(null=True, blank=True)
    oxygen_saturation = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="recorded_vitals")
    recorded_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    class Category(models.TextChoices):
        LOW_STOCK = "LOW_STOCK", "Low medicine stock"
        EXPIRED_MEDICINE = "EXPIRED_MEDICINE", "Expired medicine"
        APPOINTMENT = "APPOINTMENT", "Appointment"
        LABORATORY = "LABORATORY", "Laboratory"
        BILLING = "BILLING", "Billing"
        OTHER = "OTHER", "Other"

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    category = models.CharField(max_length=24, choices=Category.choices)
    title = models.CharField(max_length=160)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
