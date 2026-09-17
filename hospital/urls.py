from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdmissionViewSet,
    AppointmentViewSet,
    BedViewSet,
    DashboardView,
    DepartmentViewSet,
    DoctorViewSet,
    MedicalRecordViewSet,
    MedicineViewSet,
    NurseViewSet,
    PatientViewSet,
    PrescriptionViewSet,
    RoomViewSet,
    StockMovementViewSet,
    LaboratoryTestViewSet,
    InvoiceViewSet,
    PaymentViewSet,
    InsuranceProviderViewSet,
    InsuranceClaimViewSet,
    InventoryItemViewSet,
    InventoryMovementViewSet,
    VitalSignViewSet,
    NotificationViewSet,
    ReportsView,
)

router = DefaultRouter()
router.register("departments", DepartmentViewSet)
router.register("patients", PatientViewSet)
router.register("doctors", DoctorViewSet)
router.register("nurses", NurseViewSet)
router.register("rooms", RoomViewSet)
router.register("beds", BedViewSet)
router.register("appointments", AppointmentViewSet)
router.register("admissions", AdmissionViewSet)
router.register("medical-records", MedicalRecordViewSet)
router.register("prescriptions", PrescriptionViewSet)
router.register("medicines", MedicineViewSet)
router.register("stock-movements", StockMovementViewSet)
router.register("laboratory-tests", LaboratoryTestViewSet)
router.register("invoices", InvoiceViewSet)
router.register("payments", PaymentViewSet)
router.register("insurance-providers", InsuranceProviderViewSet)
router.register("insurance-claims", InsuranceClaimViewSet)
router.register("inventory-items", InventoryItemViewSet)
router.register("inventory-movements", InventoryMovementViewSet)
router.register("vital-signs", VitalSignViewSet)
router.register("notifications", NotificationViewSet, basename="notifications")

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("reports/summary/", ReportsView.as_view(), name="reports-summary"),
    path("", include(router.urls)),
]
