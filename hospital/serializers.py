from rest_framework import serializers

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
    Notification,
    Patient,
    Payment,
    Prescription,
    Room,
    StockMovement,
    VitalSign,
)


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"
        read_only_fields = ("patient_id", "registration_date")


class DoctorSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Doctor
        fields = "__all__"
        read_only_fields = ("doctor_id", "user_name", "department_name")


class NurseSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Nurse
        fields = "__all__"
        read_only_fields = ("nurse_id", "user_name", "department_name")


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"


class BedSerializer(serializers.ModelSerializer):
    room_label = serializers.CharField(source="room.number", read_only=True)

    class Meta:
        model = Bed
        fields = "__all__"
        read_only_fields = ("room_label",)


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.CharField(source="doctor.user.get_full_name", read_only=True)

    class Meta:
        model = Appointment
        fields = "__all__"
        read_only_fields = ("patient_name", "doctor_name", "created_at")

    def get_patient_name(self, instance):
        return f"{instance.patient.first_name} {instance.patient.last_name}"


class AdmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admission
        fields = "__all__"


class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = "__all__"
        read_only_fields = ("created_at",)


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = "__all__"
        read_only_fields = ("prescription_date",)


class MedicineSerializer(serializers.ModelSerializer):
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Medicine
        fields = "__all__"
        read_only_fields = ("is_low_stock",)


class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = "__all__"
        read_only_fields = ("created_by", "created_at")


class LaboratoryTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaboratoryTest
        fields = "__all__"


class InvoiceItemSerializer(serializers.ModelSerializer):
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = InvoiceItem
        fields = "__all__"


class InvoiceSerializer(serializers.ModelSerializer):
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    paid_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    outstanding_balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Invoice
        fields = "__all__"
        read_only_fields = ("invoice_number", "issued_at", "total", "paid_amount", "outstanding_balance")


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ("received_by", "payment_date")


class InsuranceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceProvider
        fields = "__all__"


class InsuranceClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceClaim
        fields = "__all__"


class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = "__all__"


class InventoryMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryMovement
        fields = "__all__"
        read_only_fields = ("created_by", "created_at")


class VitalSignSerializer(serializers.ModelSerializer):
    class Meta:
        model = VitalSign
        fields = "__all__"
        read_only_fields = ("recorded_by", "recorded_at")


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ("recipient", "created_at")
