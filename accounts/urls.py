from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    LoginView,
    LogoutView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegistrationView,
    UserManagementViewSet,
)

router = DefaultRouter()
router.register("users", UserManagementViewSet, basename="users")

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("register/", RegistrationView.as_view(), name="register"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path("password-reset/<uid>/<token>/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("", include(router.urls)),
]
