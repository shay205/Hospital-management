from rest_framework.permissions import BasePermission


class IsAdministratorOrReadOnly(BasePermission):
    administrator_roles = {"SUPER_ADMINISTRATOR", "HOSPITAL_ADMINISTRATOR"}

    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role in self.administrator_roles


class CanAccessMedicalRecords(BasePermission):
    read_roles = {"SUPER_ADMINISTRATOR", "HOSPITAL_ADMINISTRATOR", "DOCTOR", "RECORDS_OFFICER"}

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in self.read_roles

    def has_object_permission(self, request, view, obj):
        if request.user.role in {"SUPER_ADMINISTRATOR", "HOSPITAL_ADMINISTRATOR", "RECORDS_OFFICER"}:
            return True
        return getattr(getattr(obj, "doctor", None), "user_id", None) == request.user.id
