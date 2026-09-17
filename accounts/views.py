from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import AuditLog

from .models import User
from .serializers import (
    LoginSerializer,
    ManagedUserSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegistrationSerializer,
    UserSerializer,
)


class IsHospitalAdministrator(permissions.BasePermission):
    allowed_roles = {User.Role.SUPER_ADMINISTRATOR, User.Role.HOSPITAL_ADMINISTRATOR}

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in self.allowed_roles


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        login(request, user)
        AuditLog.objects.create(user=user, action="LOGIN", module="AUTH", record_id=str(user.pk), ip_address=request.META.get("REMOTE_ADDR"))
        return Response({"token": token.key, "user": UserSerializer(user).data})


class LogoutView(APIView):
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        AuditLog.objects.create(user=request.user, action="LOGOUT", module="AUTH", record_id=str(request.user.pk), ip_address=request.META.get("REMOTE_ADDR"))
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(email__iexact=serializer.validated_data["email"], is_active=True).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            send_mail(
                "Careline password reset",
                f"Use this reset link token with uid {uid}: {token}",
                None,
                [user.email],
                fail_silently=True,
            )
        return Response({"detail": "If an account matches that email, reset instructions have been sent."})


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, uid, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(pk=force_str(urlsafe_base64_decode(uid)))
        except (User.DoesNotExist, TypeError, ValueError, OverflowError):
            return Response({"detail": "Invalid or expired reset link."}, status=status.HTTP_400_BAD_REQUEST)
        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Invalid or expired reset link."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=("password", "updated_at"))
        return Response({"detail": "Password has been reset."})


class UserManagementViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("username")
    serializer_class = ManagedUserSerializer
    permission_classes = [IsHospitalAdministrator]
    search_fields = ("username", "first_name", "last_name", "email")
    filterset_fields = ("role", "is_active", "is_staff")
