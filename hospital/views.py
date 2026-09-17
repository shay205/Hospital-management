from django.db import models
from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import AuditLog

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
from .permissions import CanAccessMedicalRecords, IsAdministratorOrReadOnly
from .serializers import (
    AdmissionSerializer,
    AppointmentSerializer,
    BedSerializer,
    DepartmentSerializer,
    DoctorSerializer,
    MedicalRecordSerializer,
    MedicineSerializer,
    NurseSerializer,
    PatientSerializer,
    PaymentSerializer,
    PrescriptionSerializer,
    RoomSerializer,
    StockMovementSerializer,
    LaboratoryTestSerializer,
    InvoiceSerializer,
    InsuranceProviderSerializer,
    InsuranceClaimSerializer,
    InventoryItemSerializer,
    InventoryMovementSerializer,
    VitalSignSerializer,
    NotificationSerializer,
)


class AuditedModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdministratorOrReadOnly]

    def log_action(self, action, record_id):
        AuditLog.objects.create(user=self.request.user, action=action, module=self.__class__.__name__.replace("ViewSet", "").upper(), record_id=str(record_id), ip_address=self.request.META.get("REMOTE_ADDR"))

    def perform_create(self, serializer):
        instance = serializer.save()
        self.log_action("CREATE", instance.pk)

    def perform_update(self, serializer):
        instance = serializer.save()
        self.log_action("UPDATE", instance.pk)

    def perform_destroy(self, instance):
        record_id = str(instance.pk)
        instance.delete()
        self.log_action("DELETE", record_id)


class DepartmentViewSet(AuditedModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    search_fields = ("name", "code")
    ordering_fields = ("name", "code")


class PatientViewSet(AuditedModelViewSet):
    queryset = Patient.objects.filter(is_active=True)
    serializer_class = PatientSerializer
    search_fields = ("patient_id", "first_name", "last_name", "phone", "email")
    filterset_fields = ("gender", "blood_group", "is_active")
    ordering_fields = ("last_name", "registration_date")


class DoctorViewSet(AuditedModelViewSet):
    queryset = Doctor.objects.select_related("user", "department")
    serializer_class = DoctorSerializer
    search_fields = ("doctor_id", "user__first_name", "user__last_name", "specialization", "license_number")
    filterset_fields = ("department", "status")


class NurseViewSet(AuditedModelViewSet):
    queryset = Nurse.objects.select_related("user", "department")
    serializer_class = NurseSerializer
    search_fields = ("nurse_id", "user__first_name", "user__last_name", "license_number")
    filterset_fields = ("department", "shift", "status")


class RoomViewSet(AuditedModelViewSet):
    queryset = Room.objects.select_related("ward")
    serializer_class = RoomSerializer
    search_fields = ("number", "ward__name", "ward__code")
    filterset_fields = ("ward",)


class BedViewSet(AuditedModelViewSet):
    queryset = Bed.objects.select_related("room", "room__ward")
    serializer_class = BedSerializer
    search_fields = ("number", "room__number")
    filterset_fields = ("status", "room")


class AppointmentViewSet(AuditedModelViewSet):
    queryset = Appointment.objects.select_related("patient", "doctor__user", "department")
    serializer_class = AppointmentSerializer
    search_fields = ("patient__patient_id", "patient__first_name", "patient__last_name", "doctor__user__last_name", "reason")
    filterset_fields = ("status", "doctor", "department", "starts_at")
    ordering_fields = ("starts_at", "status")


class AdmissionViewSet(AuditedModelViewSet):
    queryset = Admission.objects.select_related("patient", "doctor__user", "bed__room")
    serializer_class = AdmissionSerializer
    search_fields = ("patient__patient_id", "patient__first_name", "patient__last_name", "diagnosis")
    filterset_fields = ("status", "doctor", "bed")
    ordering_fields = ("admitted_at", "discharged_at")


class MedicalRecordViewSet(AuditedModelViewSet):
    queryset = MedicalRecord.objects.select_related("patient", "doctor__user")
    serializer_class = MedicalRecordSerializer
    search_fields = ("patient__patient_id", "patient__first_name", "patient__last_name", "diagnosis", "symptoms")
    filterset_fields = ("patient", "doctor", "visit_date")
    ordering_fields = ("visit_date",)
    permission_classes = [CanAccessMedicalRecords]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.role == "DOCTOR":
            return queryset.filter(doctor__user=self.request.user)
        return queryset


class PrescriptionViewSet(AuditedModelViewSet):
    queryset = Prescription.objects.select_related("patient", "doctor__user")
    serializer_class = PrescriptionSerializer
    search_fields = ("patient__patient_id", "patient__first_name", "patient__last_name", "medication")
    filterset_fields = ("patient", "doctor", "status")
    ordering_fields = ("prescription_date", "status")


class MedicineViewSet(AuditedModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    search_fields = ("name", "supplier", "batch_number")
    filterset_fields = ("expiry_date",)
    ordering_fields = ("name", "stock_quantity", "expiry_date")


class StockMovementViewSet(AuditedModelViewSet):
    queryset = StockMovement.objects.select_related("medicine", "created_by")
    serializer_class = StockMovementSerializer
    filterset_fields = ("medicine", "movement_type")

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        self.log_action("CREATE", instance.pk)


class LaboratoryTestViewSet(AuditedModelViewSet):
    queryset = LaboratoryTest.objects.select_related("patient", "doctor__user", "technician")
    serializer_class = LaboratoryTestSerializer
    search_fields = ("patient__patient_id", "patient__first_name", "patient__last_name", "test_type", "result")
    filterset_fields = ("status", "doctor", "technician", "test_date")


class InvoiceViewSet(AuditedModelViewSet):
    queryset = Invoice.objects.select_related("patient").prefetch_related("items", "payments")
    serializer_class = InvoiceSerializer
    search_fields = ("invoice_number", "patient__patient_id", "patient__first_name", "patient__last_name")
    filterset_fields = ("status", "patient", "due_date")
    ordering_fields = ("issued_at", "due_date", "status")


class PaymentViewSet(AuditedModelViewSet):
    queryset = Payment.objects.select_related("patient", "invoice", "received_by")
    serializer_class = PaymentSerializer
    search_fields = ("invoice__invoice_number", "reference_number", "patient__patient_id")
    filterset_fields = ("payment_method", "invoice", "patient", "payment_date")

    def perform_create(self, serializer):
        instance = serializer.save(received_by=self.request.user)
        self.log_action("CREATE", instance.pk)


class InsuranceProviderViewSet(AuditedModelViewSet):
    queryset = InsuranceProvider.objects.all()
    serializer_class = InsuranceProviderSerializer
    search_fields = ("name", "contact_phone", "contact_email")
    filterset_fields = ("is_active",)


class InsuranceClaimViewSet(AuditedModelViewSet):
    queryset = InsuranceClaim.objects.select_related("patient", "provider", "invoice")
    serializer_class = InsuranceClaimSerializer
    search_fields = ("patient__patient_id", "provider__name", "invoice__invoice_number")
    filterset_fields = ("status", "provider", "patient")


class InventoryItemViewSet(AuditedModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    search_fields = ("item", "category", "supplier")
    filterset_fields = ("category", "expiry_date")


class InventoryMovementViewSet(AuditedModelViewSet):
    queryset = InventoryMovement.objects.select_related("item", "created_by")
    serializer_class = InventoryMovementSerializer
    filterset_fields = ("item", "movement_type")

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        self.log_action("CREATE", instance.pk)


class VitalSignViewSet(AuditedModelViewSet):
    queryset = VitalSign.objects.select_related("patient", "recorded_by")
    serializer_class = VitalSignSerializer
    search_fields = ("patient__patient_id", "patient__first_name", "patient__last_name")
    filterset_fields = ("patient", "recorded_at")
    ordering_fields = ("recorded_at",)

    def perform_create(self, serializer):
        instance = serializer.save(recorded_by=self.request.user)
        self.log_action("CREATE", instance.pk)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def perform_update(self, serializer):
        serializer.save(recipient=self.request.user)


class ReportsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            "patients": Patient.objects.filter(is_active=True).count(),
            "appointments": Appointment.objects.count(),
            "admissions": Admission.objects.filter(status=Admission.Status.ADMITTED).count(),
            "revenue": Invoice.objects.exclude(status=Invoice.Status.VOID).aggregate(total=models.Sum(models.F("items__quantity") * models.F("items__unit_price"))),
            "payments": Payment.objects.aggregate(total=models.Sum("amount")),
            "bed_occupancy": {"occupied": Bed.objects.filter(status=Bed.Status.OCCUPIED).count(), "available": Bed.objects.filter(status=Bed.Status.AVAILABLE).count()},
            "laboratory_tests": LaboratoryTest.objects.count(),
        })


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        return Response({
            "total_patients": Patient.objects.filter(is_active=True).count(),
            "doctors": Doctor.objects.filter(status="ACTIVE").count(),
            "nurses": Nurse.objects.filter(status="ACTIVE").count(),
            "departments": Department.objects.filter(is_active=True).count(),
            "todays_appointments": Appointment.objects.filter(starts_at__date=today).exclude(status=Appointment.Status.CANCELLED).count(),
            "admissions": Admission.objects.filter(status=Admission.Status.ADMITTED).count(),
            "available_beds": Bed.objects.filter(status=Bed.Status.AVAILABLE).count(),
            "prescriptions": Prescription.objects.filter(status=Prescription.Status.ACTIVE).count(),
            "pending_laboratory_tests": LaboratoryTest.objects.exclude(status=LaboratoryTest.Status.COMPLETED).count(),
            "outstanding_invoices": Invoice.objects.filter(status__in=(Invoice.Status.OPEN, Invoice.Status.PARTIALLY_PAID)).count(),
            "recent_activities": AuditLog.objects.select_related("user").values("action", "module", "record_id", "created_at", "user__username")[:10],
        })
